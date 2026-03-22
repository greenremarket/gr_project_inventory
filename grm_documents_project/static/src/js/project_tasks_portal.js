/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { renderToElement } from "@web/core/utils/render";
import { _lt } from "@web/core/l10n/translation";

publicWidget.registry.ProjectTasksDocument = publicWidget.Widget.extend({
  selector: ".o_project_tasks_document, .o_project_portal_sidebar #card_header",

  start: function () {
    var def = this._super.apply(this, arguments);
    this.rpc = this.bindService("rpc");
    var $table_header = $(
      renderToElement("grm_documents_project.portal_tasks_list_header", {
        btnTxt: _lt("Download"),
      })
    );
    $table_header
      .find("button")
      .on("click", this.downloadDelivrables.bind(this));

    this.$el.prepend($table_header);

    this.$el.on("click", ".select_all", function () {
		  const $table = $(this).closest(".task-blockList");
		  const $checkboxes = $table.find("input.o_portal_task_checkbox[data-task-id]");
		  $checkboxes.prop("checked", $(this).is(":checked"));
		});

    return def;
  },

  downloadDelivrables: function () {
    try {
      const doc_ids = this.getSelectedTasks() || this.getActiveTask();
      if (doc_ids.length === 0) {
        this.displayError($('#unselectedLineErrorMsg').text());
        return;
      }
      
      // Create a hidden form and submit it to download the file
      // This avoids fetch() issues with large files
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = '/delivrable/download';
      form.style.display = 'none';
      
      // Add task_ids
      const taskIdsInput = document.createElement('input');
      taskIdsInput.type = 'hidden';
      taskIdsInput.name = 'task_ids';
      taskIdsInput.value = doc_ids;
      form.appendChild(taskIdsInput);
      
      // Add csrf_token if it exists
      if (typeof odoo !== 'undefined' && odoo.csrf_token) {
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        csrfInput.value = odoo.csrf_token;
        form.appendChild(csrfInput);
      }
      
      // Add access_token if present in URL
      const urlParams = new URLSearchParams(window.location.search);
      const accessToken = urlParams.get('access_token');
      if (accessToken) {
        const tokenInput = document.createElement('input');
        tokenInput.type = 'hidden';
        tokenInput.name = 'access_token';
        tokenInput.value = accessToken;
        form.appendChild(tokenInput);
      }
      
      // Submit the form
      document.body.appendChild(form);
      form.submit();
      document.body.removeChild(form);
      
      // Hide any previous error messages
      this.$el.find(".error-message").hide();
      
    } catch (error) {
      console.error("Download error:", error);
      this.displayError("Erreur lors du téléchargement: " + error.message);
    }
  },

  _myDocTableExists: function () {
    return this.$el.find("table.o_portal_my_doc_table").length > 0;
  },

  getSelectedTasks: function () {
    if (!this._myDocTableExists()) {
      return;
    }
    const $table = this.$el.find("table.o_portal_my_doc_table");
    var $rows = $table.find("tbody tr");
    if ($rows.length === 0) {
      return;
    }

    let doc_ids = [];
    $rows.each(function () {
      var $row = $(this);
      let $input_checkbox = $row.find("input[data-task-id]");
      if ($input_checkbox.is(":checked")) {
        doc_ids.push(parseInt($input_checkbox.attr("data-task-id")));
      }
    });

    return doc_ids;
  },

  getActiveTask: function () {
    const task_id = this.$el.find("#task_id").val();
    return task_id ? [parseInt(task_id)] : [];
  },

  displayError: function (error) {
    this.$el
      .find(".error-message")
      .text(error).show();
    this.$el
      .find(".error-section")
      .show();
  },
});
