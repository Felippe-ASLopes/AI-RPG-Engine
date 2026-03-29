from src.adapters.vector_memory import VectorMemoryAdapter

def testar_memoria_rag():
    rag = VectorMemoryAdapter()
    
    # 1. Vamos "ensinar" algumas coisas que aconteceram em turnos passados
    print("\n--- SALVANDO MEMÓRIAS ---")
    rag.add_memory("turno_10", "O Rei de Valéria foi assassinado com veneno na taça de vinho durante o banquete.")
    rag.add_memory("turno_12", "Felps comprou uma espada longa de aço na forja do anão resmungão.")
    rag.add_memory("turno_15", "A chave da masmorra secreta está escondida embaixo da estátua da praça central.")
    
    # 2. Agora, simulamos uma pergunta do jogador ou uma ação relacionada
    # Note que NÃO usamos a palavra exata "assassinado", "veneno" ou "vinho" na query
    query_jogador = "Quem matou o governante no jantar?"
    
    print(f"\n--- RECUPERANDO MEMÓRIAS PARA: '{query_jogador}' ---")
    lembrancas = rag.recall_memories(query_jogador, n_results=1)
    
    for i, lembranca in enumerate(lembrancas):
        print(f"Lembrança {i+1}: {lembranca}")
    print("------------------------------------------------------\n")

if __name__ == "__main__":
    testar_memoria_rag()