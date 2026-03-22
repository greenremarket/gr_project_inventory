from odoo.tests.common import TransactionCase, tagged
import zipfile
from io import BytesIO


@tagged("grm")
class TestProject(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env["project.project"].create(
            {
                "name": "Project 1",
                "partner_id": cls.planning_partner.id,
            }
        )

    def test_action_view_documents_project_task_initializes_folder(self):
        task = self.env["project.task"].create(
            {
                "name": "Doc Task",
                "project_id": self.project.id,
            }
        )
        self.assertFalse(task.documents_folder_id)
        task.action_view_documents_project_task()
        self.assertTrue(
            task.documents_folder_id,
            "Documents folder should be initialized after viewing documents.",
        )

    def test_get_document_folder_returns_initialized_folder(self):
        task = self.env["project.task"].create(
            {
                "name": "Folder Task",
                "project_id": self.project.id,
            }
        )
        folder = task._get_document_folder()
        self.assertEqual(
            folder.id,
            task.documents_folder_id.id,
            "Should return the initialized documents folder.",
        )

    def test_zip_delivrable_documents_returns_zip(self):
        task = self.env["project.task"].create(
            {
                "name": "Zip Task",
                "project_id": self.project.id,
            }
        )
        folder = task._init_documents_folder()
        Document = self.env["documents.document"]
        doc1 = Document.create(
            {
                "name": "file1.txt",
                "task_id": task.id,
                "raw": b"content1",
                "folder_id": folder.id,
            }
        )
        doc2 = Document.create(
            {
                "name": "file2.txt",
                "task_id": task.id,
                "raw": b"content2",
                "folder_id": folder.id,
            }
        )
        # Patch is_delivrable to return True for both
        doc1.is_delivrable = lambda: True
        doc2.is_delivrable = lambda: True
        task.document_ids |= doc1 | doc2
        filename, zip_bytes = task.zip_delivrable_documents()
        self.assertTrue(filename.endswith("_delivrables.zip"))
        with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
            self.assertIn(f"{task.name}/file1.txt", zf.namelist())
            self.assertIn(f"{task.name}/file2.txt", zf.namelist())
            self.assertEqual(zf.read(f"{task.name}/file1.txt"), b"content1")
            self.assertEqual(zf.read(f"{task.name}/file2.txt"), b"content2")

    def test_zip_delivrable_documents_no_delivrables(self):
        task = self.env["project.task"].create(
            {
                "name": "Empty Task",
                "project_id": self.project.id,
            }
        )
        filename, zip_bytes = task.zip_delivrable_documents()
        self.assertEqual(filename, "No delivrables found.")
        self.assertEqual(zip_bytes, b"")
