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

  downloadDelivrables: async function () {
    try {
      const doc_ids = this.getSelectedTasks() || this.getActiveTask();
      if (doc_ids.length === 0) {
        this.displayError($('#unselectedLineErrorMsg').text());
        return;
      }

      // Build FormData for the POST
      const formData = new FormData();
      formData.append('task_ids', doc_ids.join(','));
      if (typeof odoo !== 'undefined' && odoo.csrf_token) {
        formData.append('csrf_token', odoo.csrf_token);
      }
      const accessToken = new URLSearchParams(window.location.search).get('access_token');
      if (accessToken) formData.append('access_token', accessToken);

      // Use fetch+blob: handles large zips correctly and keeps the user on the page
      // when there are no delivrables (instead of navigating to a blank error page).
      const response = await fetch('/delivrable/download', { method: 'POST', body: formData });
      const contentType = response.headers.get('Content-Type') || '';

      if (!response.ok || !contentType.includes('application/zip')) {
        // Server returned an error or no delivrables — show inline, don't navigate away
        const msg = await response.text();
        this.displayError(msg || "Aucun livrable disponible pour cette opération.");
        return;
      }

      // Trigger browser download from the blob
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'livrables.zip';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      this.$el.find(".error-message").hide();

    } catch (error) {
      console.error("Download error:", error);
      this.displayError("Erreur lors du téléchargement : " + error.message);
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
