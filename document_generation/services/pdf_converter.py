"""
Conversor de Documentos para PDF
Suporte multiplataforma (Windows/Linux)
"""

import logging
import os
import platform
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class PDFConverter:
    """Conversor de documentos DOCX para PDF"""
    
    def __init__(self):
        self.system = platform.system()
        self.conversion_method = self._detect_conversion_method()
    
    def _detect_conversion_method(self) -> str:
        """Detecta o melhor método de conversão disponível"""
        
        if self.system == "Windows":
            try:
                import docx2pdf
                return "docx2pdf"
            except ImportError:
                logger.warning("docx2pdf não encontrado, tentando LibreOffice")
                if self._check_libreoffice():
                    return "libreoffice"
                else:
                    return "none"
        else:
            # Linux/Mac
            if self._check_libreoffice():
                return "libreoffice"
            else:
                logger.warning("LibreOffice não encontrado")
                return "none"
    
    def _check_libreoffice(self) -> bool:
        """Verifica se LibreOffice está disponível"""
        
        try:
            result = subprocess.run(
                ["libreoffice", "--version"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def convert_to_pdf(self, docx_path: str) -> str:
        """Converte arquivo DOCX para PDF"""
        
        docx_path = Path(docx_path)
        if not docx_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {docx_path}")
        
        pdf_path = docx_path.with_suffix('.pdf')
        
        try:
            if self.conversion_method == "docx2pdf":
                return self._convert_with_docx2pdf(str(docx_path), str(pdf_path))
            elif self.conversion_method == "libreoffice":
                return self._convert_with_libreoffice(str(docx_path), str(pdf_path))
            else:
                raise RuntimeError("Nenhum método de conversão disponível")
                
        except Exception as e:
            logger.error(f"Erro na conversão para PDF: {e}")
            raise
    
    def _convert_with_docx2pdf(self, docx_path: str, pdf_path: str) -> str:
        """Conversão usando docx2pdf (Windows)"""
        
        try:
            from docx2pdf import convert
            convert(docx_path, pdf_path)
            
            if os.path.exists(pdf_path):
                logger.info(f"Conversão PDF concluída: {pdf_path}")
                return pdf_path
            else:
                raise RuntimeError("Arquivo PDF não foi criado")
                
        except Exception as e:
            logger.error(f"Erro na conversão com docx2pdf: {e}")
            raise
    
    def _convert_with_libreoffice(self, docx_path: str, pdf_path: str) -> str:
        """Conversão usando LibreOffice headless"""
        
        try:
            # Diretório de saída
            output_dir = Path(docx_path).parent
            
            # Comando LibreOffice
            cmd = [
                "libreoffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(output_dir),
                docx_path
            ]
            
            # Executar conversão
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # Timeout de 60 segundos
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"LibreOffice falhou: {result.stderr}")
            
            # Verificar se arquivo foi criado
            if os.path.exists(pdf_path):
                logger.info(f"Conversão PDF concluída: {pdf_path}")
                return pdf_path
            else:
                raise RuntimeError("Arquivo PDF não foi criado pelo LibreOffice")
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("Timeout na conversão com LibreOffice")
        except Exception as e:
            logger.error(f"Erro na conversão com LibreOffice: {e}")
            raise
    
    def batch_convert(self, docx_files: list) -> dict:
        """Converte múltiplos arquivos DOCX para PDF"""
        
        results = {
            'success': [],
            'failed': []
        }
        
        for docx_file in docx_files:
            try:
                pdf_file = self.convert_to_pdf(docx_file)
                results['success'].append({
                    'docx': docx_file,
                    'pdf': pdf_file
                })
            except Exception as e:
                results['failed'].append({
                    'docx': docx_file,
                    'error': str(e)
                })
        
        return results
    
    def get_conversion_info(self) -> dict:
        """Retorna informações sobre o sistema de conversão"""
        
        return {
            'system': self.system,
            'conversion_method': self.conversion_method,
            'available': self.conversion_method != "none",
            'libreoffice_available': self._check_libreoffice(),
            'docx2pdf_available': self.conversion_method == "docx2pdf"
        }

# Instância global
pdf_converter = PDFConverter() 