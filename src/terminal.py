import time
from jarvis_core import jarvis

def iniciar_terminal():
    print("="*60)
    print("JARVIS ONLINE - Acesso Direto via Terminal")
    print("Digite 'sair', 'exit' ou aperte Ctrl+C para desligar o sistema.")
    print("="*60)

    while True:
        try:
            # Recebe o comando do usuário
            entrada_usuario = input("\n Usuário: ")

            # Condição de parada graciosa
            if entrada_usuario.lower() in ['sair', 'exit', 'desligar']:
                print("JARVIS: Encerrando sistemas locais. Bom trabalho, senhor Stark.")
                break

            # Evita que o bot tente processar um "Enter" vazio
            if not entrada_usuario.strip():
                continue

            print("JARVIS: Pensando...")

            # Chama o Agente Master
            resposta = jarvis(entrada_usuario)

            # Imprime a resposta formatada
            print(f"\n JARVIS:\n{resposta}")
            time.sleep(0.5) # Pausa na resposta

        except KeyboardInterrupt:
            # Captura o Ctrl+C no terminal do VS Code/Linux perfeitamente
            print("\n\n JARVIS: Interrupção forçada detectada (Ctrl+C). Desligando sistemas.")
            break

if __name__ == "__main__":
    iniciar_terminal()
