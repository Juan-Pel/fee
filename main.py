#!/usr/bin/env python3
"""
Stock Market Tycoon - Simulador de Mercado Bursátil

Un simulador competitivo donde los jugadores representan corporaciones
que buscan expandirse mediante compra de acciones, fusiones y absorciones.

Modos de juego:
- Rápida (15 min): 2-4 jugadores, mayor valor de mercado gana
- Estándar (30-45 min): 3-6 jugadores, alcanzar 50 puntos de influencia
- Extendida (90 min): 4-8 jugadores, controlar 3 sectores + capital

Autor: Stock Market Tycoon Team
"""

import sys
from game.game import StockMarketGame, GameMode
from modes.quick import QuickMode
from modes.standard import StandardMode
from modes.extended import ExtendedMode


def print_welcome():
    """Muestra la pantalla de bienvenida"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        📈  STOCK MARKET TYCOON  📈                        ║
║                                                           ║
║     Simulador de Mercado Bursátil                         ║
║                                                           ║
║     Compite como una corporación en un mercado dinámico   ║
║     lleno de oportunidades y riesgos.                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)


def print_menu():
    """Muestra el menú principal"""
    print("\n=== MENÚ PRINCIPAL ===")
    print("1. Nueva Partida Rápida (15 min)")
    print("2. Nueva Partida Estándar (30-45 min)")
    print("3. Nueva Partida Extendida (90 min)")
    print("4. Ver Instrucciones")
    print("5. Salir")
    print()


def print_game_menu():
    """Muestra el menú de acciones del juego"""
    print("\n=== ACCIONES ===")
    print("[C] Comprar acciones")
    print("[V] Vender acciones")
    print("[P] Ver mi portafolio")
    print("[M] Ver mercado")
    print("[L] Ver clasificación")
    print([K])
    print("[S] Saltar turno")
    print("[Q] Salir al menú")
    print()


def show_instructions():
    """Muestra las instrucciones del juego"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                    INSTRUCCIONES                          ║
╚═══════════════════════════════════════════════════════════╝

📊 OBJETIVO DEL JUEGO
---------------------
Conviértete en el magnate dominante del mercado bursátil mediante:
• Compra y venta estratégica de acciones
• Fusiones y adquisiciones de empresas
• Gestión inteligente de tu liquidez

🎮 MECÁNICAS PRINCIPALES
------------------------
• Cada jugador empieza con capital inicial ($10,000-$20,000 según modo)
• Compra acciones cuando estén bajas, vende cuando estén altas
• Obtén mayoría (>50%) en empresas para ganar influencia
• Fusiona empresas del mismo sector que controles
• Usa cartas especiales para ventajas estratégicas
• Reacciona a eventos del mercado (crisis, booms, regulaciones)

📇 CARTAS
---------
Las cartas se obtienen cada ciertas rondas y permiten:
• Descuentos en compras
• Primas en ventas
• Adquisiciones hostiles
• Información privilegiada
• Rescates financieros

🏆 CONDICIONES DE VICTORIA
--------------------------
• Rápida: Mayor valor neto al finalizar el tiempo
• Estándar: Alcanzar 50 puntos de influencia primero
• Extendida: Controlar 3 sectores + $100,000 de capital

💡 CONSEJOS
-----------
• Mantén siempre algo de efectivo para oportunidades
• Diversifica tu portafolio entre sectores
• Observa las tendencias del mercado
• No inviertas todo en un solo sector
• Las fusiones dan bonus de influencia

¡Buena suerte, magnate! 🤑
    """)
    input("Presiona Enter para continuar...")


def setup_game(mode: str) -> StockMarketGame:
    """Configura una nueva partida"""
    
    if mode == 'quick':
        game = QuickMode()
    elif mode == 'standard':
        game = StandardMode()
    elif mode == 'extended':
        game = ExtendedMode()
    else:
        game = StockMarketGame('standard')
    
    # Añadir jugadores
    print(f"\n=== CONFIGURAR {game.mode_config['name'].upper()} ===")
    print(f"Jugadores recomendados: {game.mode_config['min_players']}-{game.mode_config['max_players']}")
    print(f"Objetivo: {game.mode_config['objective']}")
    print()
    
    num_players = int(input("Número de jugadores humanos (1-8): ") or "2")
    num_players = max(1, min(num_players, 8))
    
    for i in range(num_players):
        name = input(f"Nombre del jugador {i+1}: ") or f"Jugador {i+1}"
        game.add_player(f"player{i+1}", name, is_ai=False)
    
    # Añadir bots si hay menos de 2 jugadores
    total_players = len(game.players)
    if total_players < 2:
        bots_needed = 2 - total_players
        bot_names = ["CorpBot Alpha", "CorpBot Beta", "CorpBot Gamma", "CorpBot Delta"]
        for i in range(bots_needed):
            game.add_player(f"bot{i+1}", bot_names[i], is_ai=True)
    
    print(f"\n✓ Partida configurada con {len(game.players)} jugadores")
    return game


def display_market(game: StockMarketGame):
    """Muestra el estado del mercado"""
    print("\n" + "="*60)
    print("  📊 MERCADO BURSÁTIL")
    print("="*60)
    print(f"Ronda: {game.round_number}/{game.max_rounds}")
    print()
    
    # Mostrar sectores
    print("SECTORES:")
    for sector_name, sector in game.market.sectors.items():
        change_symbol = "📈" if sector.value_change >= 0 else "📉"
        print(f"  {change_symbol} {sector.name}: ${sector.current_value:.2f} ({sector.value_change:+.1f}%)")
    
    print("\nEMPRESAS DESTACADAS:")
    companies = sorted(game.market.companies.values(), key=lambda c: c.price_change, reverse=True)[:5]
    for company in companies:
        if company.status.value == "Activa":
            change_symbol = "↑" if company.price_change >= 0 else "↓"
            print(f"  {company.name} ({company.sector.name}): ${company.current_price:.2f} {change_symbol} {abs(company.price_change):.1f}%")
    
    print()


def display_portfolio(game: StockMarketGame, player_id: str):
    """Muestra el portafolio de un jugador"""
    player = game.get_player(player_id)
    if not player:
        print("Jugador no encontrado")
        return
    
    print("\n" + "="*60)
    print(f"  💼 PORTAFOLIO DE {player.name.upper()}")
    print("="*60)
    print(f"Efectivo: ${player.cash:,.2f}")
    print(f"Valor de mercado: ${player.market_value:,.2f}")
    print(f"Valor neto total: ${player.net_worth:,.2f}")
    print(f"Puntos de influencia: {player.influence_points}")
    print(f"Empresas controladas: {len(player.companies_owned)}")
    print(f"Sectores dominados: {len(player.sectors_controlled)}")
    
    if player.shares:
        print("\nACCIONES EN PORTAFOLIO:")
        for company_id, quantity in player.shares.items():
            company = game.market.get_company(company_id)
            if company:
                value = quantity * company.current_price
                percentage = (quantity / company.total_shares) * 100
                print(f"  • {company.name}: {quantity} acciones (${value:,.2f}) - {percentage:.1f}%")
    
    if player.cards:
        print(f"\nCARTAS ({len(player.cards)}):")
        for card_id in player.cards[:5]:
            card = game.card_deck.get_card(card_id)
            if card:
                print(f"  • {card.name}")
        if len(player.cards) > 5:
            print(f"  ... y {len(player.cards) - 5} más")
    
    print()


def display_leaderboard(game: StockMarketGame):
    """Muestra la clasificación"""
    print("\n" + "="*60)
    print("  🏆 CLASIFICACIÓN")
    print("="*60)
    
    leaderboard = game.get_leaderboard()
    
    print(f"{'#':<3} {'Jugador':<20} {'Valor Neto':<15} {'Influencia':<12} {'Estado':<10}")
    print("-"*60)
    
    for entry in leaderboard:
        status = "💀" if entry['is_bankrupt'] else "✅"
        print(f"{entry['rank']:<3} {entry['name']:<20} ${entry['net_worth']:>12,.2f} {entry['influence']:>10} {status:>8}")
    
    print()


def buy_shares_action(game: StockMarketGame, player_id: str):
    """Acción de comprar acciones"""
    player = game.get_player(player_id)
    if not player:
        return
    
    print("\n=== COMPRAR ACCIONES ===")
    print(f"Tu efectivo: ${player.cash:,.2f}")
    print()
    
    # Listar empresas disponibles
    print("EMPRESAS DISPONIBLES:")
    for i, (cid, company) in enumerate(game.market.companies.items()):
        if company.status.value == "Activa":
            affordable = int(player.cash / company.current_price)
            print(f"[{i+1}] {company.name} ({company.sector.name}) - ${company.current_price:.2f} | Disponibles: {company.available_shares} | Puedes comprar: {affordable}")
    
    try:
        choice = input("\nSelecciona empresa (número o ID): ").strip()
        
        # Buscar empresa
        company = None
        if choice.isdigit():
            idx = int(choice) - 1
            companies_list = [c for c in game.market.companies.values() if c.status.value == "Activa"]
            if 0 <= idx < len(companies_list):
                company = companies_list[idx]
        else:
            company = game.market.get_company(choice)
        
        if not company:
            print("Empresa no encontrada")
            return
        
        quantity = int(input(f"Cantidad a comprar (máx {min(company.available_shares, int(player.cash / company.current_price))}): ") or "0")
        
        if quantity <= 0:
            print("Cantidad inválida")
            return
        
        success, cost, message = game.buy_shares(player_id, company.company_id, quantity)
        
        if success:
            print(f"✓ {message}")
            print(f"  Costo total: ${cost:,.2f}")
            print(f"  Efectivo restante: ${player.cash:,.2f}")
        else:
            print(f"✗ {message}")
    
    except ValueError:
        print("Entrada inválida")


def sell_shares_action(game: StockMarketGame, player_id: str):
    """Acción de vender acciones"""
    player = game.get_player(player_id)
    if not player:
        return
    
    if not player.shares:
        print("No tienes acciones para vender")
        return
    
    print("\n=== VENDER ACCIONES ===")
    print(f"Tu efectivo actual: ${player.cash:,.2f}")
    print()
    
    # Listar acciones del jugador
    print("TUS ACCIONES:")
    for i, (cid, quantity) in enumerate(player.shares.items()):
        company = game.market.get_company(cid)
        if company:
            value = quantity * company.current_price
            print(f"[{i+1}] {company.name}: {quantity} acciones @ ${company.current_price:.2f} = ${value:,.2f}")
    
    try:
        choice = input("\nSelecciona empresa (número o ID): ").strip()
        
        # Buscar empresa
        company_id = None
        if choice.isdigit():
            idx = int(choice) - 1
            shares_list = list(player.shares.keys())
            if 0 <= idx < len(shares_list):
                company_id = shares_list[idx]
        else:
            if choice in player.shares:
                company_id = choice
        
        if not company_id or company_id not in player.shares:
            print("No tienes acciones de esa empresa")
            return
        
        quantity = int(input(f"Cantidad a vender (máx {player.shares[company_id]}): ") or "0")
        
        if quantity <= 0:
            print("Cantidad inválida")
            return
        
        success, value, message = game.sell_shares(player_id, company_id, quantity)
        
        if success:
            print(f"✓ {message}")
            print(f"  Ganancia: ${value:,.2f}")
            print(f"  Nuevo efectivo: ${player.cash:,.2f}")
        else:
            print(f"✗ {message}")
    
    except ValueError:
        print("Entrada inválida")


def play_turn(game: StockMarketGame, player_id: str):
    """Ejecuta el turno de un jugador"""
    player = game.get_player(player_id)
    if not player or player.is_bankrupt:
        print(f"{player.name if player else 'Jugador'} está en bancarrota. Turno saltado.")
        game.next_turn()
        return
    
    print("\n" + "="*60)
    print(f"  TURNO DE: {player.name}")
    print("="*60)
    print(f"Efectivo: ${player.cash:,.2f} | Influencia: {player.influence_points}")
    print()
    
    while True:
        print_game_menu()
        action = input("Tu acción: ").strip().lower()
        
        if action == 'c':
            buy_shares_action(game, player_id)
        elif action == 'v':
            sell_shares_action(game, player_id)
        elif action == 'p':
            display_portfolio(game, player_id)
        elif action == 'm':
            display_market(game)
        elif action == 'l':
            display_leaderboard(game)
        elif action == 'k':
            # Ver cartas y usar
            if player.cards:
                print("\nCARTAS DISPONIBLES:")
                for i, card_id in enumerate(player.cards):
                    card = game.card_deck.get_card(card_id)
                    if card:
                        print(f"[{i+1}] {card.name} - {card.description}")
                
                try:
                    choice = input("\nUsar carta (número o Enter para cancelar): ").strip()
                    if choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(player.cards):
                            card_id = player.cards[idx]
                            target = input("Objetivo (ID de empresa/jugador, o Enter para ninguno): ").strip() or None
                            result = game.play_card(player_id, card_id, target)
                            print(f"{'✓' if result['success'] else '✗'} {result['message']}")
                            for effect in result.get('effects', []):
                                print(f"  → {effect}")
                except ValueError:
                    print("Entrada inválida")
            else:
                print("No tienes cartas")
        elif action == 's':
            print("Turno saltado")
            break
        elif action == 'q':
            confirm = input("¿Salir al menú principal? (s/n): ").strip().lower()
            if confirm == 's':
                return 'quit'
        else:
            print("Acción inválida")
            continue
        
        # Verificar si el jugador quiere terminar su turno
        if action in ['c', 'v', 'k']:
            cont = input("\n¿Continuar acciones? (s/n): ").strip().lower()
            if cont != 's':
                break
    
    game.next_turn()
    return None


def run_game(game: StockMarketGame):
    """Ejecuta el bucle principal del juego"""
    print("\n" + "="*60)
    print("  ¡QUE COMIENCE EL JUEGO!")
    print("="*60)
    
    while not game.game_over:
        current_player = game.get_current_player()
        
        print(f"\n{'='*60}")
        print(f"  RONDA {game.round_number} - Turno de {current_player.name}")
        print(f"{'='*60}")
        
        if current_player.is_ai:
            # Turno simple de IA (aleatorio básico)
            print(f"🤖 {current_player.name} está pensando...")
            
            # IA básica: comprar si tiene dinero, vender aleatoriamente
            if current_player.cash > 5000 and game.market.companies:
                # Intentar comprar una acción aleatoria
                available_companies = [c for c in game.market.companies.values() 
                                      if c.status.value == "Activa" and c.available_shares > 0]
                if available_companies:
                    company = available_companies[0]
                    quantity = min(10, int(current_player.cash / company.current_price))
                    if quantity > 0:
                        success, cost, msg = game.buy_shares(current_player.player_id, 
                                                            company.company_id, quantity)
                        if success:
                            print(f"  → {current_player.name} compró {quantity} acciones de {company.name}")
            
            game.next_turn()
        else:
            result = play_turn(game, current_player.player_id)
            if result == 'quit':
                return
    
    # Juego terminado
    print("\n" + "="*60)
    print("  🏁 JUEGO TERMINADO")
    print("="*60)
    
    if game.winner:
        winner = game.get_player(game.winner)
        print(f"\n🎉 ¡GANADOR: {winner.name}! 🎉")
        print(f"   Valor neto: ${winner.net_worth:,.2f}")
        print(f"   Influencia: {winner.influence_points}")
    else:
        print("\n¡Empate técnico!")
    
    # Mostrar clasificación final
    display_leaderboard(game)


def main():
    """Función principal"""
    print_welcome()
    
    while True:
        print_menu()
        choice = input("Selecciona una opción: ").strip()
        
        if choice == '1':
            game = setup_game('quick')
            run_game(game)
        elif choice == '2':
            game = setup_game('standard')
            run_game(game)
        elif choice == '3':
            game = setup_game('extended')
            run_game(game)
        elif choice == '4':
            show_instructions()
        elif choice == '5':
            print("\n¡Gracias por jugar Stock Market Tycoon! 👋")
            print("¡Hasta pronto, magnate! 📈\n")
            break
        else:
            print("Opción inválida. Intenta de nuevo.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nJuego interrumpido. ¡Hasta luego! 👋")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        print("Por favor reporta este error.")
        sys.exit(1)
