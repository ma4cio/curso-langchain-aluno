"""
Sistema de rate limiting para controlar requisições à API do Google Gemini.
Limite: 15 requisições por minuto
"""

import time
from collections import deque
from threading import Lock
from typing import Optional

class RateLimiter:
    """Controlador de taxa de requisições."""
    
    def __init__(self, max_requests: int = 15, time_window: int = 60):
        """
        Inicializa o rate limiter.
        
        Args:
            max_requests: Número máximo de requisições permitidas
            time_window: Janela de tempo em segundos (padrão: 60 segundos)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.lock = Lock()
    
    def can_make_request(self) -> bool:
        """
        Verifica se é possível fazer uma nova requisição.
        
        Returns:
            True se pode fazer requisição, False caso contrário
        """
        with self.lock:
            current_time = time.time()
            
            # Remove requisições antigas (fora da janela de tempo)
            while self.requests and self.requests[0] <= current_time - self.time_window:
                self.requests.popleft()
            
            # Verifica se ainda há espaço para nova requisição
            return len(self.requests) < self.max_requests
    
    def wait_if_needed(self) -> float:
        """
        Aguarda se necessário para respeitar o limite de taxa.
        
        Returns:
            Tempo de espera em segundos (0 se não precisou esperar)
        """
        with self.lock:
            current_time = time.time()
            
            # Remove requisições antigas
            while self.requests and self.requests[0] <= current_time - self.time_window:
                self.requests.popleft()
            
            # Se ainda há espaço, não precisa esperar
            if len(self.requests) < self.max_requests:
                return 0.0
            
            # Calcula quanto tempo precisa esperar
            oldest_request = self.requests[0]
            wait_time = (oldest_request + self.time_window) - current_time
            
            if wait_time > 0:
                print(f"Rate limit atingido. Aguardando {wait_time:.1f} segundos...")
                time.sleep(wait_time)
                return wait_time
            
            return 0.0
    
    def record_request(self) -> None:
        """Registra uma nova requisição."""
        with self.lock:
            self.requests.append(time.time())
    
    def get_remaining_requests(self) -> int:
        """
        Retorna o número de requisições restantes na janela atual.
        
        Returns:
            Número de requisições que ainda podem ser feitas
        """
        with self.lock:
            current_time = time.time()
            
            # Remove requisições antigas
            while self.requests and self.requests[0] <= current_time - self.time_window:
                self.requests.popleft()
            
            return max(0, self.max_requests - len(self.requests))
    
    def get_reset_time(self) -> Optional[float]:
        """
        Retorna o tempo até o reset do contador.
        
        Returns:
            Tempo em segundos até o reset, ou None se não há requisições
        """
        with self.lock:
            if not self.requests:
                return None
            
            current_time = time.time()
            oldest_request = self.requests[0]
            return max(0, (oldest_request + self.time_window) - current_time)
    
    def get_status(self) -> dict:
        """
        Retorna o status atual do rate limiter.
        
        Returns:
            Dicionário com informações sobre o status
        """
        with self.lock:
            current_time = time.time()
            
            # Remove requisições antigas
            while self.requests and self.requests[0] <= current_time - self.time_window:
                self.requests.popleft()
            
            remaining = self.get_remaining_requests()
            reset_time = self.get_reset_time()
            
            return {
                'max_requests': self.max_requests,
                'time_window': self.time_window,
                'current_requests': len(self.requests),
                'remaining_requests': remaining,
                'reset_time': reset_time,
                'can_make_request': remaining > 0
            }

# Instância global do rate limiter
rate_limiter = RateLimiter(max_requests=15, time_window=60)

def check_rate_limit() -> bool:
    """
    Verifica se pode fazer uma requisição e aguarda se necessário.
    
    Returns:
        True se pode prosseguir, False se deve abortar
    """
    if not rate_limiter.can_make_request():
        wait_time = rate_limiter.wait_if_needed()
        if wait_time > 0:
            print(f"Aguardou {wait_time:.1f} segundos para respeitar o rate limit.")
    
    rate_limiter.record_request()
    return True

def get_rate_limit_status() -> dict:
    """
    Retorna o status atual do rate limiter.
    
    Returns:
        Dicionário com informações sobre o status
    """
    return rate_limiter.get_status()

def print_rate_limit_status() -> None:
    """Imprime o status atual do rate limiter."""
    status = get_rate_limit_status()
    
    print(f"\n--- Status do Rate Limiter ---")
    print(f"Requisições atuais: {status['current_requests']}/{status['max_requests']}")
    print(f"Requisições restantes: {status['remaining_requests']}")
    
    if status['reset_time']:
        print(f"Reset em: {status['reset_time']:.1f} segundos")
    else:
        print("Contador limpo")
    
    print(f"Pode fazer requisição: {'Sim' if status['can_make_request'] else 'Não'}")
    print("---" + "-" * 25)
