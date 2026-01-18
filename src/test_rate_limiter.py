"""
Script de teste para demonstrar o funcionamento do rate limiter.
"""

import time
from rate_limiter import check_rate_limit, print_rate_limit_status, get_rate_limit_status

def test_rate_limiter():
    """Testa o funcionamento do rate limiter."""
    print("=== Teste do Rate Limiter ===")
    print("Limite: 15 requisições por minuto")
    print("Testando 20 requisições rápidas...\n")
    
    for i in range(20):
        print(f"Requisição {i+1}/20:")
        
        # Verificar se pode fazer requisição
        if check_rate_limit():
            print("  ✓ Requisição permitida")
        else:
            print("  ✗ Requisição bloqueada")
        
        # Mostrar status a cada 5 requisições
        if (i + 1) % 5 == 0:
            print_rate_limit_status()
            print()
        
        # Pequena pausa para visualizar
        time.sleep(0.1)
    
    print("\n=== Teste Concluído ===")
    print_rate_limit_status()

def test_wait_functionality():
    """Testa a funcionalidade de espera."""
    print("\n=== Teste de Espera ===")
    print("Fazendo 16 requisições para testar a espera...\n")
    
    for i in range(16):
        print(f"Requisição {i+1}/16:")
        
        if check_rate_limit():
            print("  ✓ Requisição permitida")
        else:
            print("  ✗ Requisição bloqueada - aguardando...")
        
        time.sleep(0.1)
    
    print("\n=== Teste de Espera Concluído ===")
    print_rate_limit_status()

def monitor_status():
    """Monitora o status do rate limiter em tempo real."""
    print("\n=== Monitor de Status ===")
    print("Monitorando por 70 segundos...")
    print("Pressione Ctrl+C para parar\n")
    
    try:
        for i in range(70):
            status = get_rate_limit_status()
            print(f"Tempo: {i:2d}s | Requisições: {status['current_requests']:2d}/{status['max_requests']} | Restantes: {status['remaining_requests']:2d} | Reset em: {status['reset_time']:.1f}s")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitor interrompido pelo usuário.")
    
    print("\n=== Monitor Concluído ===")
    print_rate_limit_status()

if __name__ == "__main__":
    print("Escolha um teste:")
    print("1. Teste básico (20 requisições)")
    print("2. Teste de espera (16 requisições)")
    print("3. Monitor de status (70 segundos)")
    print("4. Todos os testes")
    
    choice = input("\nDigite sua escolha (1-4): ").strip()
    
    if choice == "1":
        test_rate_limiter()
    elif choice == "2":
        test_wait_functionality()
    elif choice == "3":
        monitor_status()
    elif choice == "4":
        test_rate_limiter()
        test_wait_functionality()
        monitor_status()
    else:
        print("Escolha inválida. Executando teste básico...")
        test_rate_limiter()
