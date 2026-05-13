import webview
import json
from game.game import StockMarketGame
from modes import QuickMode, StandardMode, ExtendedMode

class StockMarketAPI:
    def __init__(self):
        self.game = None
        self.window = None

    def create_game(self, mode_name, player_names_json):
        """Crea una nueva partida desde la UI"""
        try:
            player_names = json.loads(player_names_json)
            
            # Crear instancia del modo
            if mode_name == 'quick':
                mode_instance = QuickMode()
            elif mode_name == 'extended':
                mode_instance = ExtendedMode()
            else:
                mode_instance = StandardMode()
            
            # Iniciar juego con el modo
            self.game = StockMarketGame(mode=mode_instance.mode_config['name'].lower())
            
            # Añadir jugadores
            for i, name in enumerate(player_names):
                self.game.add_player(f"player_{i}", name, is_ai=False)
            
            return json.dumps({"status": "success", "message": "Partida creada"})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def get_game_state(self):
        """Obtiene el estado actual completo para renderizar"""
        if not self.game:
            return json.dumps({"error": "No game active"})
        
        # Obtener empresas por sector
        market_data = {}
        for sector_name, sector in self.game.market.sectors.items():
            market_data[sector_name] = {
                "companies": [
                    {
                        "id": comp.company_id,
                        "name": comp.name,
                        "price": comp.current_price,
                        "total_shares": comp.total_shares,
                        "available_shares": comp.available_shares
                    } for comp in sector.companies.values()
                ]
            }
        
        state = {
            "round": self.game.round_number,
            "current_player": self.game.current_player_idx,
            "players": [
                {
                    "id": pid,
                    "name": p.name,
                    "cash": p.cash,
                    "portfolio": dict(p.shares),
                    "influence": p.influence_points,
                    "bankrupt": p.is_bankrupt,
                    "cards": list(p.cards)
                } for pid, p in self.game.players.items()
            ],
            "market": market_data,
            "events": self.game.event_manager.event_log[-5:] if hasattr(self.game.event_manager, 'event_log') else []
        }
        return json.dumps(state)

    def buy_stock(self, player_idx, company_id, quantity):
        """Ejecuta compra de acciones"""
        if not self.game: 
            return json.dumps({"status": "error", "message": "No game"})
        try:
            player_ids = list(self.game.players.keys())
            player_id = player_ids[player_idx]
            success, cost, msg = self.game.buy_shares(player_id, company_id, int(quantity))
            return json.dumps({"status": "success" if success else "error", "message": msg, "cost": cost})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def sell_stock(self, player_idx, company_id, quantity):
        """Ejecuta venta de acciones"""
        if not self.game: 
            return json.dumps({"status": "error", "message": "No game"})
        try:
            player_ids = list(self.game.players.keys())
            player_id = player_ids[player_idx]
            success, value, msg = self.game.sell_shares(player_id, company_id, int(quantity))
            return json.dumps({"status": "success" if success else "error", "message": msg, "value": value})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def next_turn(self):
        """Pasa al siguiente turno y procesa eventos"""
        if not self.game: 
            return json.dumps({"status": "error", "message": "No game"})
        self.game.next_turn()
        return self.get_game_state()

    def trigger_event(self):
        """Fuerza un evento de mercado"""
        if not self.game: 
            return json.dumps({"status": "error", "message": "No game"})
        event = self.game.event_manager.generate_event(self.game.round_number)
        if event:
            msg = self.game.event_manager.apply_event(event, self.game.market)
            return json.dumps({"status": "success", "message": msg, "event": event.name})
        return json.dumps({"status": "info", "message": "No event triggered"})

def run_web_app():
    api = StockMarketAPI()
    
    # Crear ventana
    window = webview.create_window(
        'Stock Market Tycoon - Dashboard',
        'dashboard.html', # Archivo local
        js_api=api,
        width=1280,
        height=800,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600)
    )
    
    api.window = window
    
    # Iniciar servidor web embebido
    webview.start(debug=True)

if __name__ == '__main__':
    run_web_app()
