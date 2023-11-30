import unittest
from unittest.mock import patch, MagicMock

import requests
from requests import RequestException

from protein_data_handler.fasta import FastaDownloader


class TestFastaDownloader(unittest.TestCase):

    def setUp(self):
        self.session_mock = MagicMock()  # Simula la sesión de SQLAlchemy
        self.downloader = FastaDownloader(self.session_mock,'test_dir')

    def test_init(self):
        self.assertEqual(self.downloader.session, self.session_mock)

    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_creacion_directorio_si_no_existe(self, mock_exists, mock_makedirs):
        # Configurar el mock para simular que el directorio no existe
        mock_exists.return_value = False

        # Inicializar FastaDownloader
        FastaDownloader('sesion_falsa', 'ruta/directorio')

        # Verificar que os.makedirs fue llamado
        mock_makedirs.assert_called_once_with('ruta/directorio', exist_ok=True)


    def test_download_fastas_invalid_input(self):
        with self.assertRaises(ValueError):
            self.downloader.download_fastas("no-list")

    @patch('protein_data_handler.fasta.requests.get')
    def test_download_fasta_successful(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "fake-fasta-content"
        mock_get.return_value = mock_response

        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            self.downloader.download_fasta("PDBID")
            mock_file.assert_called_with("test_dir/PDBID.fasta", "w")
            mock_file().write.assert_called_with("fake-fasta-content")

    @patch('protein_data_handler.fasta.requests.get')
    @patch('protein_data_handler.fasta.logging.error')
    def test_download_fasta_http_error(self, mock_logging_error, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("HTTP error")

        self.downloader.download_fasta("PDBID")
        mock_logging_error.assert_called_with("Error al descargar FASTA para PDBID: HTTP error")

    @patch('protein_data_handler.fasta.requests.get')
    @patch('protein_data_handler.fasta.logging.error')
    def test_download_fasta_io_error(self, mock_logging_error, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "fake-fasta-content"
        mock_get.return_value = mock_response

        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            mock_file.side_effect = IOError("IO error")
            self.downloader.download_fasta("PDBID")
            mock_logging_error.assert_called_with("Error al escribir el archivo para PDBID: IO error")

    @patch('protein_data_handler.fasta.FastaDownloader.download_fasta')
    def test_download_fastas(self, mock_download_fasta):
        pdb_ids = ["PDB1", "PDB2", "PDB3"]
        self.downloader.download_fastas(pdb_ids)
        self.assertEqual(mock_download_fasta.call_count, len(pdb_ids))

    def test_download_fasta_invalid_pdb_id(self):
        with self.assertRaises(ValueError):
            self.downloader.download_fasta(123)

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_download_fasta_directory_creation(self, mock_makedirs, mock_exists):
        mock_exists.return_value = None
        mock_makedirs.return_value = None

        self.downloader.download_fasta("PDBID")
        mock_exists.return_value = True
        mock_makedirs.return_value = True

        self.downloader.download_fasta("PDBID")


if __name__ == '__main__':
    unittest.main()
