import flet as ft
import asyncio
from binance.client import Client
import time
import threading
import os
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import base64
from google import genai
from google.genai import types
import ta


def main(page: ft.Page):
    
    page.title = "Binance AI"
    page.version = "0.7"
    page.description = "Binance AI"
    
    # Настройки PWA (Progressive Web Application)
    page.assets_dir = "assets"
    page.manifest = "manifest.json" 
    
    # Настройки интерфейса
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = 'center'
    page.vertical_alignment = 'center'
    page.adaptive = False  # Отключаем адаптивный дизайн
    page.language = "ua"
    page.favicon = "favicon.png"
    page.fonts = {"default": "Roboto"}
    page.padding = 5
    page.bgcolor = ft.Colors.BLACK

    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')

    # Создание объекта клиента Binance
    # Создание объекта клиента Binance
    client = Client(api_key, api_secret)

    # Создание объекта клиента Google GenAI
    client_ai = genai.Client(api_key="AIzaSyBcL44-3Iqf3sRZ3COHynGs5mGogjWqnmc",)
    neuro_result_text = ft.Markdown("Анализ нейросети: Ожидание данных...")


    
    # Контейнер для страницы графика
    graph_container = ft.Container(
        height=0,  # Начальная высота 0 (будет изменена анимацией)
        animate=ft.Animation(duration=250, curve="decelerate"),
        padding=ft.padding.all(10),
        content=ft.Column(
            controls=[
                ft.Text("График пары ETH/USDT", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                # Создание объекта графика
                chart := ft.LineChart(
                    data_series=[],  # Изначально пустые данные
                    border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.ON_SURFACE)),
                    left_axis=ft.ChartAxis(
                        title=ft.Text("Price (USDT)"),
                        labels_size=40,
                    ),

                ),
                # --- Контейнер для прокручиваемого текста ---
                ft.Container(
                    padding=ft.padding.all(20),
                    content=ft.Column(
                        controls=[
                            neuro_result_text, # Здесь твой текстовый элемент
                            ft.Container(height=200),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        spacing=10, # Расстояние между строками текста (если neuro_result_text содержит переносы)
                    ),
                    expand=True, # Позволяет контейнеру занимать доступное пространство в Column
                ),
            ],
            spacing=10,
            expand=True, # Позволит основному Column занимать все доступное пространство
        )
    )

    def workspace_page(): 
        return ft.Container(
            height=0,  # Начальная высота 0
            animate=ft.Animation(duration=250, curve="decelerate"),
            content=ft.Column(
                controls=[
                    ft.Text("Настройки"),
                ]
            )
        )

    def signals_page():
        return ft.Container(
            height=0,  # Начальная высота 0
            animate=ft.Animation(duration=250, curve="decelerate"),
            content=ft.Column(
                controls=[
                    ft.Text("Сигнали"),

                ]
            )
        )

    def workspace_page():
        return ft.Container(
            height=0,  # Начальная высота 0
            animate=ft.Animation(duration=250, curve="decelerate"),
            content=ft.Column(
                controls=[
                    ft.Text("Настройки"),

                ]
            )
        )
        
    
    async def on_nav_change(e):
        selected_index = e.control.selected_index
        for i, container in enumerate(page.controls[1:4]):
            container.height = page.height if i == selected_index else 0
            container.update()
        await asyncio.sleep(0.5)  # Задержка для плавного перехода

    # Создание верхней панели приложения
    top_appbar = ft.AppBar(
        title=ft.Text(   
            "Binance AI", 
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_600
        ),
        actions=[
            ft.IconButton(
                ft.CupertinoIcons.INFO,
                style=ft.ButtonStyle(padding=0)
            )
        ],
        bgcolor=ft.Colors.with_opacity(1, ft.Colors.BLACK),
    )

    # Создание нижней навигационной панели
    bottom_navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                bgcolor=ft.Colors.BLUE_500,
                icon=ft.Icon(
                    ft.Icons.SHOW_CHART,
                    size=30,
                    color=ft.Colors.BLUE_300
                ),
                label="График"
            ),
            ft.NavigationBarDestination(
                bgcolor=ft.Colors.BLUE_500,
                icon=ft.Icon(ft.Icons.NOTIFICATIONS,
                size=30, 
                color=ft.Colors.BLUE_300
                ),
                label="Сигналы"
            ),
            ft.NavigationBarDestination(
                bgcolor=ft.Colors.BLUE_500,
                icon=ft.Icon(ft.Icons.SETTINGS,
                 size=30,
                  color=ft.Colors.BLUE_300
                  ),
                label="Настройки"
            ),
        ],
        bgcolor=ft.Colors.with_opacity(1, ft.Colors.BLACK45),
        label_behavior=ft.NavigationBarLabelBehavior.ONLY_SHOW_SELECTED,
        on_change=on_nav_change
    )

    # Добавляем элементы на страницу
    page.add(top_appbar)
    page.add(graph_container) # Добавляем контейнер графика
    page.add(signals_page())
    page.add(workspace_page())
    page.add(bottom_navigation_bar)

    # Установка начальной страницы
    # Устанавливаем высоту graph_container
    page.controls[1].height = page.height
    page.controls[1].update()

    # Функция для обновления данных графика в отдельном потоке
    def update_chart_data_thread():
        while True:
            try:
                # Get hourly price data for ETH/USDT
                # klines = client.get_historical_klines("ETHUSDT", Client.KLINE_INTERVAL_1HOUR, "1 day ago UTC")
                klines = client.futures_klines(symbol="ETHUSDT", interval=Client.KLINE_INTERVAL_15MINUTE, limit=96)
                df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df['close'] = df['close'].astype(float)

                # Convert price data to ft.LineChartDataPoint objects
                data_points = [ft.LineChartDataPoint(i, row['close']) for i, row in df.iterrows()]

                # Обновляем UI в основном потоке с помощью page.run_thread
                def update_ui():
                    chart.data_series = [
                        ft.LineChartData(
                            data_points=data_points,
                            stroke_width=2,
                            color=ft.Colors.BLUE_ACCENT_700,
                            stroke_cap_round=True,
                        ),
                    ]
                    if not df.empty:
                        chart.min_y = df['close'].min()
                        chart.max_y = df['close'].max()
                        chart.max_x = len(df) + len(df) * 0.1
            
                    else: # Обработка случая пустых данных
                         chart.min_y = 0
                         chart.max_y = 1
                         chart.max_x = 100
                    page.update()

                page.run_thread(update_ui)

            except Exception as e:
                print(f"Error updating chart data in thread: {e}")
            time.sleep(5)  # Wait for 5 seconds


    def generate_ai_analysis_stream():
        # --- 1. Получение и обработка данных ETH/USDT ---
        try:
            klines_1h = client.futures_klines(symbol="ETHUSDT", interval=Client.KLINE_INTERVAL_1HOUR, limit=720)
            df_1h = pd.DataFrame(klines_1h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

            df_1h[['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']] = \
                df_1h[['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']].astype(float)
            df_1h['timestamp'] = pd.to_datetime(df_1h['timestamp'], unit='ms')

            # --- Добавление технических индикаторов для 1-часового интервала ---
            df_1h['SMA_20'] = ta.trend.sma_indicator(df_1h['close'], window=20)
            df_1h['SMA_50'] = ta.trend.sma_indicator(df_1h['close'], window=50)
            df_1h['RSI'] = ta.momentum.rsi(df_1h['close'], window=14)
            df_1h['MACD'] = ta.trend.macd(df_1h['close'])
            df_1h['MACD_Signal'] = ta.trend.macd_signal(df_1h['close'])
            df_1h['MACD_Diff'] = ta.trend.macd_diff(df_1h['close'])
            bollinger_bands_1h = ta.volatility.BollingerBands(df_1h['close'], window=20, window_dev=2)
            df_1h['BB_Upper'] = bollinger_bands_1h.bollinger_hband()
            df_1h['BB_Lower'] = bollinger_bands_1h.bollinger_lband()


            # --- Извлечение ключевой информации, индикаторов, уровней и объемов для 1-часового интервала ---
            latest_price_1h = df_1h['close'].iloc[-1]
            open_price_24h_ago_1h = df_1h['open'].iloc[0]
            price_change_24h_1h = ((latest_price_1h - open_price_24h_ago_1h) / open_price_24h_ago_1h) * 100 if open_price_24h_ago_1h != 0 else 0
            
            highest_price_1h = df_1h['high'].max() # Максимум за период
            lowest_price_1h = df_1h['low'].min()   # Минимум за период

            recent_resistance_1h = df_1h['high'].iloc[-5:].max() # Макс. High за последние 5 свечей
            recent_support_1h = df_1h['low'].iloc[-5:].min()     # Мин. Low за последние 5 свечей
            
            total_volume_24h_1h = df_1h['volume'].sum()
            average_volume_per_hour_1h = df_1h['volume'].mean()
            latest_volume_1h = df_1h['volume'].iloc[-1]
            latest_taker_buy_volume_1h = df_1h['taker_buy_base_asset_volume'].iloc[-1]
            latest_taker_buy_ratio_1h = (latest_taker_buy_volume_1h / latest_volume_1h) * 100 if latest_volume_1h != 0 else 0

            latest_sma20_1h = df_1h['SMA_20'].iloc[-1]
            latest_sma50_1h = df_1h['SMA_50'].iloc[-1]
            latest_rsi_1h = df_1h['RSI'].iloc[-1]
            latest_macd_1h = df_1h['MACD'].iloc[-1]
            latest_macd_signal_1h = df_1h['MACD_Signal'].iloc[-1]
            latest_macd_diff_1h = df_1h['MACD_Diff'].iloc[-1]
            latest_bb_upper_1h = bollinger_bands_1h.bollinger_hband().iloc[-1]
            latest_bb_lower_1h = bollinger_bands_1h.bollinger_lband().iloc[-1]

            # --- Получение и обработка данных для 15-минутного интервала ---
            klines_15m = client.futures_klines(symbol="ETHUSDT", interval=Client.KLINE_INTERVAL_15MINUTE, limit=1500) # 24 часа * 4 свечи/час = 96 свечей
            df_15m = pd.DataFrame(klines_15m, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

            df_15m[['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']] = \
                df_15m[['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']].astype(float)
            df_15m['timestamp'] = pd.to_datetime(df_15m['timestamp'], unit='ms')

            # --- Добавление технических индикаторов для 15-минутного интервала ---
            df_15m['SMA_20'] = ta.trend.sma_indicator(df_15m['close'], window=20)
            df_15m['SMA_50'] = ta.trend.sma_indicator(df_15m['close'], window=50)
            df_15m['RSI'] = ta.momentum.rsi(df_15m['close'], window=14)
            df_15m['MACD'] = ta.trend.macd(df_15m['close'])
            df_15m['MACD_Signal'] = ta.trend.macd_signal(df_15m['close'])
            df_15m['MACD_Diff'] = ta.trend.macd_diff(df_15m['close'])
            bollinger_bands_15m = ta.volatility.BollingerBands(df_15m['close'], window=20, window_dev=2)
            df_15m['BB_Upper'] = bollinger_bands_15m.bollinger_hband()
            df_15m['BB_Lower'] = bollinger_bands_15m.bollinger_lband()


            # --- Извлечение ключевой информации, индикаторов, уровней и объемов для 15-минутного интервала ---
            latest_price_15m = df_15m['close'].iloc[-1]
            open_price_24h_ago_15m = df_15m['open'].iloc[0]
            price_change_24h_15m = ((latest_price_15m - open_price_24h_ago_15m) / open_price_24h_ago_15m) * 100 if open_price_24h_ago_15m != 0 else 0
            
            highest_price_15m = df_15m['high'].max() 
            lowest_price_15m = df_15m['low'].min()   

            recent_resistance_15m = df_15m['high'].iloc[-5:].max() 
            recent_support_15m = df_15m['low'].iloc[-5:].min()     
            
            total_volume_24h_15m = df_15m['volume'].sum()
            average_volume_per_15m = df_15m['volume'].mean()
            latest_volume_15m = df_15m['volume'].iloc[-1]
            latest_taker_buy_volume_15m = df_15m['taker_buy_base_asset_volume'].iloc[-1]
            latest_taker_buy_ratio_15m = (latest_taker_buy_volume_15m / latest_volume_15m) * 100 if latest_volume_15m != 0 else 0

            latest_sma20_15m = df_15m['SMA_20'].iloc[-1]
            latest_sma50_15m = df_15m['SMA_50'].iloc[-1]
            latest_rsi_15m = df_15m['RSI'].iloc[-1]
            latest_macd_15m = df_15m['MACD'].iloc[-1]
            latest_macd_signal_15m = df_15m['MACD_Signal'].iloc[-1]
            latest_macd_diff_15m = df_15m['MACD_Diff'].iloc[-1]
            latest_bb_upper_15m = bollinger_bands_15m.bollinger_hband().iloc[-1]
            latest_bb_lower_15m = bollinger_bands_15m.bollinger_lband().iloc[-1]


            # Формируем текстовый ввод для нейросети с учетом всех данных
            input_for_ai = (
                f"Анализ графика ETH/USDT (часовой интервал, последние 24 часа):\n"
                f"Текущая цена: {latest_price_1h:.6f} USDT.\n"
                f"Изменение за 24ч: {price_change_24h_1h:.6f}%.\n"
                f"Исторический максимум за 24ч: {highest_price_1h:.6f} USDT, минимум: {lowest_price_1h:.6f} USDT.\n"
                f"**Предполагаемые уровни (1ч):** Сопротивление около {recent_resistance_1h:.6f}, Поддержка около {recent_support_1h:.6f}.\n"
                f"**Объемы торгов (1ч):** Общий за 24ч: {total_volume_24h_1h:.6f}, Средний часовой: {average_volume_per_hour_1h:.6f}.\n"
                f"  Последний час: Объем {latest_volume_1h:.6f}, Из них покупки по рынку: {latest_taker_buy_volume_1h:.6f} ({latest_taker_buy_ratio_1h:.6f}%).\n"
                f"**Технические индикаторы (1ч):**\n"
                f"  SMA(20): {latest_sma20_1h:.6f}, SMA(50): {latest_sma50_1h:.6f}.\n"
                f"  RSI(14): {latest_rsi_1h:.6f} (нормально: 30-70).\n"
                f"  MACD: {latest_macd_1h:.8f}, Сигнальная линия MACD: {latest_macd_signal_1h:.8f}, Гистограмма MACD: {latest_macd_diff_1h:.8f}.\n"
                f"  Полосы Боллинджера: Верхняя {latest_bb_upper_1h:.6f}, Нижняя {latest_bb_lower_1h:.6f}.\n\n"

                f"Анализ графика ETH/USDT (15-минутный интервал, последние 24 часа):\n"
                f"Текущая цена: {latest_price_15m:.6f} USDT.\n"
                f"Изменение за 24ч: {price_change_24h_15m:.6f}%.\n"
                f"Исторический максимум за 24ч: {highest_price_15m:.6f} USDT, минимум: {lowest_price_15m:.6f} USDT.\n"
                f"**Предполагаемые уровни (15м):** Сопротивление около {recent_resistance_15m:.6f}, Поддержка около {recent_support_15m:.6f}.\n"
                f"**Объемы торгов (15м):** Общий за 24ч: {total_volume_24h_15m:.6f}, Средний 15-минутный: {average_volume_per_15m:.6f}.\n"
                f"  Последние 15 минут: Объем {latest_volume_15m:.6f}, Из них покупки по рынку: {latest_taker_buy_volume_15m:.6f} ({latest_taker_buy_ratio_15m:.6f}%).\n"
                f"**Технические индикаторы (15м):**\n"
                f"  SMA(20): {latest_sma20_15m:.6f}, SMA(50): {latest_sma50_15m:.6f}.\n"
                f"  RSI(14): {latest_rsi_15m:.6f} (нормально: 30-70).\n"
                f"  MACD: {latest_macd_15m:.8f}, Сигнальная линия MACD: {latest_macd_signal_15m:.8f}, Гистограмма MACD: {latest_macd_diff_15m:.8f}.\n"
                f"  Полосы Боллинджера: Верхняя {latest_bb_upper_15m:.6f}, Нижняя {latest_bb_lower_15m:.6f}.\n"
                f"Делай анализ основаясь на данных как по часу так и за 15 минут\n"
            )

        except Exception as e:
            print(f"Ошибка при получении, обработке данных, расчете индикаторов или уровней: {e}")
            input_for_ai = "Не удалось получить или обработать все данные по ETH/USDT, включая индикаторы, уровни и объемы. Точка входа неопределенна. Используй эмоции"
            yield input_for_ai
            return

        # --- 2. Вызов модели AI с подготовленным вводом (без изменений) ---
        model = "gemini-2.5-flash-lite-preview-06-17"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=input_for_ai),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            thinking_config = types.ThinkingConfig(
                thinking_budget=-1,
            ),
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text="""Роль: Ты трейдер-аналитик. 
    Твоя задача — анализировать графики и новости, чтобы определять возможные точки входа.

    Инструкция:

    Основываясь на техническом анализе графика и релевантных новостях, определи возможную точку входа.

    Примеры (для тебя):

    Запрос: \"Анализ BTC/USD, 4ч. Что по входу?\" Твой ответ: \"BTC/USD: Покупка в диапазоне $65,000 - $65,500.\"
    Запрос: \"Акции Tesla, 1д. Новости по продажам. Где вход?\" Твой ответ: \"TSLA: Продажа около $180.\"
    Запрос: \"EUR/USD, 1ч. Рынок во флэте. Точка входа?\" Твой ответ: \"Точка входа неопределенна.\""""),
            ],
        )

        for chunk in client_ai.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            yield chunk.text

    # --- Изменения в функции update_ai_result_thread() ---
    def update_ai_result_thread():
        while True:
            try:
                # Сбрасываем текст перед новым анализом, если нужно
                current_analysis_text = ""
                neuro_result_text.value = "" # Очищаем поле перед новым выводом
                page.update() # Обновляем UI, чтобы очистка была видна
                
                # Получаем анализ по частям
                for chunk_text in generate_ai_analysis_stream(): # Используем новую функцию
                    current_analysis_text += chunk_text

                    # Обновляем UI в основном потоке с каждой новой частью
                    def update_ui_chunk():
                        neuro_result_text.value = current_analysis_text
                        page.update()

                    page.run_thread(update_ui_chunk)
                    time.sleep(1) # Небольшая задержка для эффекта "печатания"
                
            except Exception as e:
                neuro_result_text.value = f"Нейросеть пока отдыхает. Пречина: {e}"
                print(f"Error updating AI result in thread: {e}")

            time.sleep(300) # Ждем 300 секунд перед следующим запросом


    # Запускаем поток обновления данных графика
    update_thread = threading.Thread(target=update_chart_data_thread, daemon=True)
    update_thread.start()
    # Запускаем поток обновления данных графика
    update_thread = threading.Thread(target=update_ai_result_thread, daemon=True)
    update_thread.start()

if __name__ == "__main__":
    """
    Точка входа в приложение.
    Запускает приложение с указанной директорией ассетов.
    """
    # ft.app(main, assets_dir="assets")

    # Альтернативный запуск в веб-браузере:
    ft.app(main,
        assets_dir="assets", 
        view=ft.AppView.WEB_BROWSER, 
        port=9002
        # port=1026
     )