from abc import ABC, abstractmethod

from telegram.ext import ContextTypes
from telegram import Update


class IBotHandlers(ABC):
    
    @abstractmethod
    def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE)-> None: 
        pass

    @abstractmethod
    def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE)-> None: 
        pass

    @abstractmethod
    async def ruta_programada_hoy(self, update: Update, context: ContextTypes.DEFAULT_TYPE)-> None: 
        pass

    @abstractmethod
    async def ruta_despachados(self, update: Update, context: ContextTypes.DEFAULT_TYPE)-> None: 
        pass