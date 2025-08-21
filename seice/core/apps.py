from django.apps import AppConfig
import threading
import time
import logging

logger = logging.getLogger(__name__)

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Inicia a coleta SIMPLES de logs quando o Django iniciar
        """
        # Importar o sistema simples
        from .coleta_simples import iniciar_coleta_automatica
        
        def delayed_start():
            time.sleep(3)  # Aguarda 3 segundos
            try:
                iniciar_coleta_automatica()
                logger.info("🎉 SISTEMA SIMPLES: Coleta de presenças iniciada!")
            except Exception as e:
                logger.error(f"❌ Erro: {e}")
        
        # Iniciar em thread separada
        startup_thread = threading.Thread(target=delayed_start, daemon=True)
        startup_thread.start()
        
        logger.info("📱 Sistema SIMPLES de presenças carregado!")
