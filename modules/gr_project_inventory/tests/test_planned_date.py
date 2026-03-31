# -*- coding: utf-8 -*-
"""
Tests for planned_date_begin persistence in task creation.

Root cause: enterprise's _onchange_planned_dates (project_enterprise/models/project_task.py)
clears planned_date_begin client-side when date_deadline is empty:
    if not self.date_deadline:
        self.planned_date_begin = False

This fires in the browser AND via Odoo's Form() test helper, but NOT via raw create().
These tests use Form() to faithfully reproduce browser onchange behavior.
"""

import unittest
from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase, tagged, Form
from odoo.exceptions import ValidationError


@tagged('-at_install', 'post_install')
class TestPlannedDatePersistence(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.project = cls.env['project.project'].search([('name', '=', 'General')], limit=1)
        if not cls.project:
            cls.project = cls.env['project.project'].create({'name': 'General'})

    def test_planned_date_begin_wiped_without_deadline(self):
        """
        Documents the root cause: setting ONLY planned_date_begin via Form()
        results in planned_date_begin=False on the saved record.

        Enterprise's _onchange_planned_dates fires and clears it because
        date_deadline is empty. This test MUST PASS (bug confirmed) before the fix
        is applied, and should still PASS after the fix because the fix is in the
        VIEW (the creation form now also collects date_deadline), not in the model.
        """
        start = datetime(2026, 4, 23, 0, 0, 0)

        with Form(self.env['project.task']) as task_form:
            task_form.name = 'Test no deadline'
            task_form.project_id = self.project
            task_form.planned_date_begin = start
            # Intentionally NOT setting date_deadline

        task = task_form.save()

        # Enterprise onchange fired and cleared planned_date_begin because
        # date_deadline was empty. This is the confirmed bug.
        self.assertFalse(
            task.planned_date_begin,
            "BUG CONFIRMED: enterprise onchange clears planned_date_begin "
            "when date_deadline is empty. The fix must be in the creation form "
            "(add date_deadline field) not in the model."
        )
        self.assertFalse(task.date_deadline)

    def test_create_syncs_planned_date_from_deadline(self):
        """
        THE FIX: when date_deadline is provided via create() (as the updated
        creation form will submit — the form now collects date_deadline, not
        planned_date_begin), our create() override mirrors it to planned_date_begin.
        Uses raw create() because the sync happens server-side, not via onchange.
        """
        from datetime import date as d
        deadline = d(2026, 4, 23)

        task = self.env['project.task'].create({
            'name': 'Test create sync',
            'project_id': self.project.id,
            'date_deadline': deadline,
            # planned_date_begin intentionally absent — create() should set it
        })

        self.assertTrue(task.planned_date_begin,
            "create() should auto-set planned_date_begin from date_deadline")
        self.assertEqual(task.planned_date_begin.date(), deadline,
            "planned_date_begin date part should match date_deadline")
        self.assertEqual(task.planned_date_begin.hour, 0)
        self.assertEqual(task.planned_date_begin.minute, 0)

    def test_explicit_planned_date_begin_is_not_overwritten(self):
        """
        If planned_date_begin is explicitly provided alongside date_deadline,
        create() must not overwrite it.
        """
        from datetime import date as d
        start = datetime(2026, 4, 23, 9, 30, 0)
        end = d(2026, 5, 10)

        task = self.env['project.task'].create({
            'name': 'Test explicit start',
            'project_id': self.project.id,
            'planned_date_begin': start,
            'date_deadline': end,
        })

        self.assertEqual(task.planned_date_begin, start,
            "Explicit planned_date_begin must not be overwritten by create()")
