# -*- coding: utf-8 -*-
"""Tests for the Aiken Workbench lot-creation hook on project.task.

All MySQL I/O is mocked so these tests run without a live Aiken connection.
"""
from unittest.mock import MagicMock, patch, call
from odoo.tests import TransactionCase


_MODULE = 'odoo.addons.gr_project_inventory.models.erasure_service.pymysql'


def _make_mock_conn(existing_lot=False, next_id=1178):
    """Return a mock pymysql connection whose cursor behaves like the real one."""
    mock_cursor = MagicMock()
    mock_cursor.__enter__ = lambda s: s
    mock_cursor.__exit__ = MagicMock(return_value=False)

    # fetchone() is called twice inside create_lot:
    #   1st call  — duplicate check  (None = no duplicate / dict = duplicate)
    #   2nd call  — MAX(LotID)+1
    duplicate_row = {'1': 1} if existing_lot else None
    mock_cursor.fetchone.side_effect = [duplicate_row, {'next_id': next_id}]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.autocommit = False
    return mock_conn, mock_cursor


class TestAikenLotCreation(TransactionCase):

    def _make_task(self, **extra):
        defaults = {
            'name': 'Test Op',
            'client_destination_name': 'DUPONT',
        }
        defaults.update(extra)
        return self.env['project.task'].create(defaults)

    # ------------------------------------------------------------------
    # create_lot() — service method
    # ------------------------------------------------------------------

    @patch(_MODULE)
    def test_create_lot_inserts_correct_row(self, mock_pymysql):
        """create_lot() must insert a row with the expected field values."""
        mock_conn, mock_cursor = _make_mock_conn(next_id=1200)
        mock_pymysql.connect.return_value = mock_conn
        mock_pymysql.cursors.DictCursor = MagicMock()

        svc = self.env['gr.erasure.service']
        svc.create_lot('TST601', 'DUPONT PARIS')

        # Verify INSERT was called
        execute_calls = mock_cursor.execute.call_args_list
        insert_call = next(
            (c for c in execute_calls if 'INSERT' in str(c)),
            None,
        )
        self.assertIsNotNone(insert_call, 'INSERT was not called')
        args = insert_call[0][1]  # positional SQL params tuple
        lot_id, number, customer, params = args[0], args[1], args[2], args[3]
        self.assertEqual(lot_id, 1200)
        self.assertEqual(number, 'TST601')
        self.assertEqual(customer, 'DUPONT PARIS')
        self.assertEqual(params, b'0' * 352)
        mock_conn.commit.assert_called_once()

    @patch(_MODULE)
    def test_create_lot_raises_on_duplicate(self, mock_pymysql):
        """create_lot() must raise (not silently skip) when the lot already exists."""
        mock_conn, mock_cursor = _make_mock_conn(existing_lot=True)
        mock_pymysql.connect.return_value = mock_conn
        mock_pymysql.cursors.DictCursor = MagicMock()

        svc = self.env['gr.erasure.service']
        with self.assertRaises(ValueError):
            svc.create_lot('EXISTING', 'SOME CLIENT')
        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()

    @patch(_MODULE)
    def test_create_lot_rollback_on_insert_error(self, mock_pymysql):
        """create_lot() must roll back and re-raise if the INSERT fails."""
        mock_conn = MagicMock()
        mock_conn.autocommit = False
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        # duplicate check → no duplicate, then raise on MAX query
        mock_cursor.fetchone.side_effect = [None, {'next_id': 1}]
        mock_cursor.execute.side_effect = [None, None, Exception('DB error')]
        mock_conn.cursor.return_value = mock_cursor
        mock_pymysql.connect.return_value = mock_conn
        mock_pymysql.cursors.DictCursor = MagicMock()

        with self.assertRaises(Exception):
            self.env['gr.erasure.service'].create_lot('FAIL', 'X')
        mock_conn.rollback.assert_called_once()

    # ------------------------------------------------------------------
    # project.task.create() — hook behaviour
    # ------------------------------------------------------------------

    @patch(_MODULE)
    def test_task_create_calls_aiken_when_flag_set(self, mock_pymysql):
        """Task creation with create_aiken_lot=True must call create_lot()."""
        mock_conn, _ = _make_mock_conn(next_id=1300)
        mock_pymysql.connect.return_value = mock_conn
        mock_pymysql.cursors.DictCursor = MagicMock()

        task = self.env['project.task'].create({
            'name': 'Op Aiken',
            'client_destination_name': 'MAIRIE',
            'create_aiken_lot': True,
        })
        self.assertTrue(task.id)
        mock_pymysql.connect.assert_called_once()

    @patch(_MODULE)
    def test_task_create_skips_aiken_when_flag_not_set(self, mock_pymysql):
        """Task creation with create_aiken_lot=False must NOT call MySQL."""
        mock_conn, _ = _make_mock_conn()
        mock_pymysql.connect.return_value = mock_conn
        mock_pymysql.cursors.DictCursor = MagicMock()

        task = self.env['project.task'].create({
            'name': 'Op No Aiken',
            'client_destination_name': 'MAIRIE',
            'create_aiken_lot': False,
        })
        self.assertTrue(task.id)
        mock_pymysql.connect.assert_not_called()

    @patch(_MODULE)
    def test_task_create_succeeds_even_if_aiken_unreachable(self, mock_pymysql):
        """MySQL connection failure must not prevent task creation."""
        mock_pymysql.connect.side_effect = Exception('Connection refused')
        mock_pymysql.cursors.DictCursor = MagicMock()

        # Should not raise — task must be created
        task = self.env['project.task'].create({
            'name': 'Op Unreachable Aiken',
            'client_destination_name': 'MAIRIE',
            'create_aiken_lot': True,
        })
        self.assertTrue(task.id, 'Task must be created even when Aiken is unreachable')

    @patch(_MODULE)
    def test_task_create_succeeds_even_if_lot_duplicate(self, mock_pymysql):
        """Duplicate lot in Aiken must not prevent task creation."""
        mock_conn, _ = _make_mock_conn(existing_lot=True)
        mock_pymysql.connect.return_value = mock_conn
        mock_pymysql.cursors.DictCursor = MagicMock()

        task = self.env['project.task'].create({
            'name': 'Op Duplicate Lot',
            'lot_name': 'EXI601',  # 6-char max constraint
            'client_destination_name': 'MAIRIE',
            'create_aiken_lot': True,
        })
        self.assertTrue(task.id, 'Task must be created even when Aiken lot already exists')

    @patch(_MODULE)
    def test_customer_priority_client_destination(self, mock_pymysql):
        """Customer label must prefer client_destination_name over other fields."""
        mock_conn, mock_cursor = _make_mock_conn(next_id=1400)
        mock_pymysql.connect.return_value = mock_conn
        mock_pymysql.cursors.DictCursor = MagicMock()

        partner = self.env['res.partner'].create({'name': 'PARTNER NAME'})
        self.env['project.task'].create({
            'name': 'Op Priority',
            'client_destination_name': 'DESTINATION WINS',
            'partner_id': partner.id,
            'create_aiken_lot': True,
        })

        insert_call = next(
            (c for c in mock_cursor.execute.call_args_list if 'INSERT' in str(c)),
            None,
        )
        self.assertIsNotNone(insert_call)
        customer_arg = insert_call[0][1][2]  # 3rd param = customer
        self.assertEqual(customer_arg, 'DESTINATION WINS')
