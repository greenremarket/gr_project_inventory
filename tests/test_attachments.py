from odoo.tests.common import TransactionCase
import base64

class TestTaskAttachments(TransactionCase):
    def setUp(self):
        super().setUp()
        # Préparation des données de test
        self.project = self.env['project.project'].create({'name': 'Test Project'})
        
    def test_task_attachments(self):
        """Test that attachments are correctly linked to tasks when using temp_attachment_ids."""
        # Utiliser un savepoint pour pouvoir revenir en arrière après le test
        self.cr.execute('SAVEPOINT test_task_attachments')
        
        try:
            # Créer un attachement temporaire avec des données binaires valides
            test_data = base64.b64encode(b'Test attachment data')
            attachment = self.env['ir.attachment'].create({
                'name': 'Test Attachment',
                'type': 'binary',
                'datas': test_data,
                'datas_fname': 'test.txt',
            })
            
            # Créer une tâche avec cet attachement
            task = self.env['project.task'].create({
                'name': 'Test Task',
                'project_id': self.project.id,
                'temp_attachment_ids': [(6, 0, [attachment.id])],
            })
            
            # Vérifier que l'attachement est correctement lié à la tâche
            self.assertEqual(attachment.res_model, 'project.task')
            self.assertEqual(attachment.res_id, task.id)
            
            # Vérifier que le contenu de l'attachement est préservé
            self.assertEqual(attachment.datas, test_data)
            
        finally:
            # Nettoyer en revenant au savepoint, peu importe si le test a réussi ou échoué
            self.cr.execute('ROLLBACK TO SAVEPOINT test_task_attachments')
    
    def tearDown(self):
        # S'assurer que le projet de test est également supprimé
        # Note: Normalement, TransactionCase fait un rollback automatique,
        # mais c'est une bonne pratique d'être explicite
        try:
            if hasattr(self, 'project') and self.project:
                self.project.unlink()
        except Exception:
            pass  # Ignorer les erreurs lors du nettoyage
        super().tearDown()
