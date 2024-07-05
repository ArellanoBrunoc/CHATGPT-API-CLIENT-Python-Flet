import flet as ft
import time as time
from dotenv import load_dotenv

from openai import OpenAI
import requests
import math
from colour import Color
def main(page: ft.Page):
    start_color = Color("#021323")
    end_color = Color("#4E499E")

    # Generamos 6 colores intermedios para una transición suave
    gradient = list(start_color.range_to(end_color, 8))

    # Convertimos los colores a formato hexadecimal con el prefijo requerido
    hex_gradient = [f"0xff{color.hex.lstrip('#')}" for color in gradient]
    load_dotenv()

    # Acceder a la variable de entorno
    with open(".env", "r") as env:
        variables = env.readlines()
        for line in variables:
            if "OPENAI_API_KEY" in line:
                openai_api_key = line.split("=")[1].replace("\n","")
            if "usuario" in line:
                usuario = line.split("=")[1]


    color_oscuro = "#021323"
    color_claro = "#A2BEDC"
    color_secundario_oscuro= "#B793C9"
    color_terciario_claro="#A2BEDC"
    color_secundario_claro="#FFFFFF"
    color_terciario_oscuro="#4E499E"
    page.bgcolor =color_oscuro

    client = OpenAI()

        
    
    
    
    # Campo de texto para ingresar el mensaje
    memoria_de_mensajes_enviados = []
    memoria_de_respuestas = []
    page.fonts ={"Monserrat": "Assets/fonts/inter.ttf"}
    page.theme = ft.Theme(font_family="Monserrat")
    x = page.width
    y = page.height
    page.window_width=x
    page.window_height=y
    page.window_max_height=y
    page.window_max_width=x
    page.padding=5
    historial = [{"role": "system", "content": f"Eres un útil asistente, el usuario se llama {usuario}"}]
    historial_actual = []
    selected_session= None
    page.theme_mode = ft.ThemeMode.DARK
    indice_historial = 0

    # Función para manejar el envío de mensajes
    def enviar_mensaje_usuario(e):
        nonlocal indice_historial
        page.appbar.title.controls.append( ft.ProgressBar(width=x/10, bgcolor=color_terciario_oscuro, color=color_secundario_oscuro))
        #recupera al mensaje de los controles de la columna principal
        mensaje = str(page.controls[0].content.controls[2].content.controls[0].value)
        if mensaje != "":
            historial.append({"role": "user", "content": mensaje})

            # Limpia el campo de texto después de enviar el mensaje
            page.controls[0].content.controls[2].content.controls[0].value = ""
            # Actualiza los controles en la página
            page.update()
            mensaje_enviado("usuario", str(mensaje))
            historial_actual.append(str(mensaje))
            indice_historial = len(historial_actual) - 1
            headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {openai_api_key}'
                    }
            data = {
                "model": "gpt-3.5-turbo-0125",
                "messages": historial
                    }
            try:
                response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
                response_data = response.json()

                page.appbar.title.controls[0] = ft.Text(f"{response_data["usage"]["total_tokens"]} Tks - CHAT GPT-3.5", color=color_terciario_claro,weight=ft.FontWeight.W_500)
            
            finally:
                
                mensaje_enviado("gpt", str(response_data["choices"][0]["message"]["content"].strip()))
                
                
        else:
            return
    def copiar_respuesta(e):
        e.control.icon_color= color_secundario_oscuro
        e.control.update()
        page.set_clipboard(e.control.data)
    def convertir_a_mes(fecha):
        meses = {
        1: "de Enero de", 2: "de Febrero de", 3: "de Marzo de", 4: "de Abril de",
        5: "de Mayo de", 6: "de Junio de", 7: "de Julio de", 8: "de Agosto de",
        9: "de Septiembre de", 10: "de Octubre de", 11: "de Noviembre de", 12:"de Diciembre dee"
    }
        fecha_int = int(fecha)
        # Devuelve el nombre del mes correspondiente al número, o None si el número no es válido.
        return meses.get(fecha_int, None)
    def cargar_memoria(e):
        valor = str(e.control.data)
        page.appbar.title.controls.append(ft.Row( [ft.ProgressBar(width=x/10, bgcolor=color_terciario_oscuro, color=color_secundario_oscuro), 
                                                ft.Text(f"Cargando historial {valor}...", size=15, weight=ft.FontWeight.W_500, color=color_terciario_claro)]))

        page.update()

        if page.client_storage.contains_key("historial"+str(valor)):
            historial_ranura = page.client_storage.get("historial"+str(valor))
            cargar_memoria_interfaz(historial_ranura)
        else:
            page.appbar.title.controls.pop()

        page.update()
    
    def cargar_memoria_interfaz(nuevo_historial):
        nonlocal historial
        page.controls[0].content.controls[1].content = ft.Column([], scroll=ft.ScrollMode.ALWAYS, auto_scroll=True, alignment=ft.MainAxisAlignment.START, spacing=10)
        for mensaje in nuevo_historial:
            if mensaje['role'] == "system":
                continue
            elif mensaje['role'] == "user":
                page.controls[0].content.controls[1].content.controls.append(ft.Container(ft.Column([ft.Text(f"Tú", color=color_terciario_claro, weight=ft.FontWeight.W_500, size=20),
                                                                                    ft.Text(mensaje['content'], color=color_secundario_claro, weight=ft.FontWeight.W_500, size=15, selectable=True)], ft.CrossAxisAlignment.END), 
                                                                                    border= ft.border.all(1, ft.colors.TRANSPARENT),padding=20,
                                                                                    border_radius=ft.border_radius.all(15), ))
            elif mensaje['role'] == "assistant":

                page.controls[0].content.controls[1].content.controls.append(ft.Container(ft.Column([ft.Row([ft.Text(f"CHAT GPT", color=color_terciario_claro, weight=ft.FontWeight.W_500, size=20), ft.IconButton(icon=ft.icons.COPY, data=mensaje['content'], icon_color=color_terciario_claro, on_click=copiar_respuesta)]),
                                                                                    ft.Text(mensaje['content'], color=color_secundario_claro, weight=ft.FontWeight.W_500, size=15, selectable=True)], ft.CrossAxisAlignment.END), 
                                                                                    border= ft.border.all(1, ft.colors.TRANSPARENT),padding=20,
                                                                                    border_radius=ft.border_radius.all(15), )) 
        historial = nuevo_historial
        page.appbar.title.controls.pop()
        page.update()
    def mensaje_enviado(tipo_de_mensaje:str, mensaje:str):

        page.update()
        # Formatear la hora local en una cadena legible
        hora_formateada = time.strftime('%d-%m-%Y %H:%M', time.localtime())
        partes =  hora_formateada.split("-")
        mes_nombre = convertir_a_mes(partes[1])
        partes[1] = mes_nombre
        fecha_hora_con_mes = "-".join(partes)
        fecha_hora_con_espacios = fecha_hora_con_mes.replace("-", " ")
        if tipo_de_mensaje == "usuario":
            page.controls[0].content.controls[1].content.controls.append(ft.Container(ft.Column([ft.Text(f"Tú       {fecha_hora_con_espacios}", color=color_terciario_claro, weight=ft.FontWeight.W_500, size=20),
                                                                                    ft.Text(mensaje, color=color_secundario_claro, weight=ft.FontWeight.W_500, size=15, selectable=True)], ft.CrossAxisAlignment.END), 
                                                                                    border= ft.border.all(1, ft.colors.TRANSPARENT),padding=20,
                                                                                    border_radius=ft.border_radius.all(15), ))
        elif tipo_de_mensaje == "gpt":
            # Contamos cuántas veces aparece "```"
            code_blocks = mensaje.count("```")

            # Si hay al menos dos bloques de código, reemplazamos el primer y segundo bloque
            if code_blocks >= 2:
                # Reemplazar la primera aparición
                mensaje = mensaje.replace("```", "---Inicio de código: ", 1)
                # Reemplazar la segunda aparición
                mensaje = mensaje.replace("```", "---Fin de código---", 1)

#            Manejar casos donde sólo hay una aparición por alguna razón
            elif code_blocks == 1:
                mensaje = mensaje.replace("```", "---Código sin fin detectado---", 1)

            page.controls[0].content.controls[1].content.controls.append(ft.Container(ft.Column([ft.Row([ft.Text(f"CHAT GPT", color=color_terciario_claro, weight=ft.FontWeight.W_500, size=20), ft.IconButton(icon=ft.icons.COPY, data=mensaje, icon_color=color_terciario_claro, on_click=copiar_respuesta)]),
                                                                                    ft.Text(mensaje, color=color_secundario_claro, weight=ft.FontWeight.W_500, size=15, selectable=True)], ft.CrossAxisAlignment.END), 
                                                                                    border= ft.border.all(1, ft.colors.TRANSPARENT),padding=20,
                                                                                    border_radius=ft.border_radius.all(15), ))     
            historial.append({"role": "assistant", "content": mensaje})
            page.appbar.title.controls.pop()
        page.update()

    def menu_icons(num:str):
        if page.client_storage.contains_key("nombresesion"+num): # True if the key exists
            nombre_pagina=page.client_storage.get("nombresesion"+num)
            icono_boton = ft.ElevatedButton(content=ft.Row([ ft.Icon(name=ft.icons.RESTORE_PAGE_SHARP),ft.Text(value=f"{nombre_pagina}", weight=ft.FontWeight.W_500)]), color={ft.MaterialState.HOVERED:color_terciario_claro, "": color_oscuro} ,on_long_press=bs_open,on_click=cargar_memoria,bgcolor={ft.MaterialState.HOVERED:color_terciario_oscuro, "": color_terciario_claro}, data=int(num), )
        else:
            icono_boton = ft.ElevatedButton(content=ft.Row([ ft.Icon(name=ft.icons.RESTORE_PAGE_SHARP),ft.Text(value=f"SESIÓN {num}", weight=ft.FontWeight.W_500)]), color={ft.MaterialState.HOVERED:color_terciario_claro, "": color_oscuro} ,on_long_press=bs_open,on_click=cargar_memoria,bgcolor={ft.MaterialState.HOVERED:color_terciario_oscuro, "": color_terciario_claro}, data=int(num), )
        return icono_boton
    def inicializador_de_interfaz_uno ():
        chat_title = ft.Container(ft.Row([ft.Row([menu_icons("1"),menu_icons("2"), menu_icons("3")])]), height=50,width=x, left=75, right=75, top=0,border= ft.border.only(bottom=ft.border.BorderSide(1, color_secundario_claro)))
        input_de_texto = ft.TextField(height=70,hint_text="Escribe tu mensaje aquí", expand=True, color="#FFFFFF",   multiline=True,autofocus=True, label="Escribe un mensaje",label_style=ft.TextStyle(color=color_claro, weight=ft.FontWeight.W_500), border_color=color_claro, 
                                    shift_enter=True,cursor_color=color_secundario_claro,on_submit=enviar_mensaje_usuario,text_style=ft.TextStyle(weight=ft.FontWeight.W_500))
        btn_enviar = ft.IconButton(icon=ft.icons.ARROW_RIGHT, on_click=enviar_mensaje_usuario, bgcolor=color_claro, icon_color= color_oscuro, )
        fila_interfaz = ft.Container(ft.Row([input_de_texto, btn_enviar], alignment=ft.alignment.top_center), height=100, bottom=0, left=100, right=100, top=y-300)
        columna_de_mensajes= ft.Container(ft.Column([], scroll=ft.ScrollMode.ALWAYS, auto_scroll=True, alignment=ft.MainAxisAlignment.START, spacing=10), 
                                        height=y*0.60,width=x-150,expand=True,top = 70, left=75, right=75 )
        interfaz = ft.Container(ft.Stack([chat_title,columna_de_mensajes, fila_interfaz], width=x, height=y ), height=y, width=x,padding=0, 
                                
                                           gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=hex_gradient,
                tile_mode=ft.GradientTileMode.MIRROR,   
                rotation=math.pi*2,
            ))
        return interfaz
    def limpiar_chat(e):
        nonlocal historial, usuario
        page.controls[0].content.controls[1].content = ft.Column([], scroll=ft.ScrollMode.ALWAYS, auto_scroll=True, alignment=ft.MainAxisAlignment.START, spacing=10)
        historial = [{"role": "system", "content": f"Eres un útil asistente, el usuario se llama {usuario}"}]
        page.appbar.title.controls[0] = ft.Text(f"0 Tks - CHAT GPT-3.5", color=color_terciario_claro, weight=ft.FontWeight.W_500)
        
        page.update()
    def change_name(e):
        nuevo_nombre = bs.content.value
        page.controls[0].content.controls[0].content.controls[0].controls[selected_session-1].content.controls[1].value = nuevo_nombre
        if page.client_storage.contains_key("nombresesion"+str(selected_session)):
            page.client_storage.remove("nombresesion"+str(selected_session))
        page.client_storage.set("nombresesion"+str(selected_session), nuevo_nombre)
        page.update()
        bs_close(e)
        
    def save_chat(e):
        nonlocal historial
        valor_crudo = str(bs3.content.value)
        valor = valor_crudo.replace(" ", "")
        if valor != "1" and valor != "2" and valor != "3":
            return
        if page.client_storage.contains_key("historial"+str(valor)):
            page.client_storage.remove("historial"+str(valor))
        page.client_storage.set("historial"+str(valor), historial)
        bs3.content.value=f"Se ha guardado con exito en la ranura {valor}"

        page.update()
        
    def change_api(e): 
        lineas = ""
        nueva_API = bs2.content.value
        if " " in nueva_API or nueva_API == "":
            return
        with open(".env", "r") as file:
            lineas = file.readlines()
            for i, linea in enumerate(lineas):
                if "OPENAI_API_KEY=" in linea:
                    lineas[i] = f'OPENAI_API_KEY={nueva_API}\n'

        with open(".env", "w") as file:
            file.writelines(lineas)
    def bs3_open(e):
        bs3.open=True
        bs3.update()
    def bs2_open(e):
        bs2.open=True
        bs2.update()
        
    def bs_open(e):
        nonlocal selected_session

        selected_session = int(e.control.data)
        bs.open=True
        bs.update()
    def bs3_close(e):
        bs3.open=False
        bs3.update()
    def bs2_close(e):
        bs2.open=False
        bs2.update()
    def bs_close(e):
        nonlocal selected_session
        selected_session = None
        bs.open=False
        bs.update()
    
    def mensaje_anterior(e):
        nonlocal historial_actual
        nonlocal indice_historial
    
        # Acceder al control de TextField donde se mostrará el mensaje
        input_texto = page.controls[0].content.controls[2].content.controls[0]

        # Establecer el valor del control a partir del historial
        if historial_actual:  # Asegúrate de que el historial no esté vacío
            input_texto.value = historial_actual[indice_historial]
        # Decrementar el índice para el siguiente uso
            indice_historial -= 1
        # Si el índice es menor que 0, se vuelve al final de la lista
            if indice_historial < 0:
                indice_historial = len(historial_actual) - 1
        # Actualizar la página para mostrar el cambio
            page.update()
        else:
        # Manejar el caso donde no hay mensajes en el historial
            input_texto.value = "No hay mensajes anteriores."
            page.update()

    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.ADJUST, color="#D26B9D"),
        leading_width=x/10,
        title=ft.Row([ft.Text("0 Tks - CHAT GPT-3.5", color=color_terciario_claro, weight=ft.FontWeight.W_500),]),
        center_title=False,
        bgcolor=ft.colors.TRANSPARENT,
                actions=[
            ft.ElevatedButton(content=(ft.Row([ft.Text("API",weight=ft.FontWeight.W_500), ft.Icon(name=ft.icons.API_ROUNDED)])), bgcolor=color_oscuro, color=color_secundario_oscuro, on_click=bs2_open),
            ft.ElevatedButton(content=(ft.Row([ft.Text("Guardar",weight=ft.FontWeight.W_500), ft.Icon(name=ft.icons.SAVE_ALT_ROUNDED)])), bgcolor=color_oscuro, color=color_secundario_oscuro, on_click=bs3_open),
            ft.ElevatedButton(content=(ft.Row([ft.Text("Limpiar",weight=ft.FontWeight.W_500), ft.Icon(name=ft.icons.CLEAR_ALL)])), bgcolor=color_oscuro, color=color_secundario_oscuro, on_click=limpiar_chat),
            ft.IconButton(icon=ft.icons.ROTATE_LEFT, bgcolor=ft.colors.TRANSPARENT, icon_color=color_secundario_oscuro, on_click=mensaje_anterior,scale=1.5),
    
        ]
    )
    bs = ft.AlertDialog(
        modal=True,
        title=ft.Text("Cambiar nombre", color=color_terciario_oscuro, weight=ft.FontWeight.W_500),
        content=ft.TextField(value="",label="Nuevo nombre",label_style=ft.TextStyle(color=color_oscuro, weight=ft.FontWeight.W_500), color="BLACK", cursor_color="BLACK",border_color=color_oscuro, text_style=ft.TextStyle(weight=ft.FontWeight.W_500)),
        actions=[
            ft.IconButton(icon=ft.icons.CHANGE_CIRCLE, scale=1.5, on_click=change_name,icon_color=color_oscuro),
            ft.IconButton(icon=ft.icons.CANCEL,scale=1.5, on_click=bs_close, icon_color=color_oscuro),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
        on_dismiss=bs_close,
        bgcolor=color_terciario_claro
    )
    
    
    
    
    bs2 = ft.AlertDialog(
        modal=True,
        title=ft.Text("Configurar API", color=color_terciario_oscuro, weight=ft.FontWeight.W_500),
        content=ft.TextField(value="",label="API",label_style=ft.TextStyle(color=color_oscuro, weight=ft.FontWeight.W_500), color="BLACK", cursor_color="BLACK",border_color=color_oscuro, text_style=ft.TextStyle(weight=ft.FontWeight.W_500)),
        actions=[
            ft.IconButton(icon=ft.icons.API_OUTLINED, scale=1.5, on_click=change_api,icon_color=color_oscuro),
            ft.IconButton(icon=ft.icons.CANCEL,scale=1.5, on_click=bs2_close, icon_color=color_oscuro),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
        on_dismiss=bs_close,
        bgcolor=color_terciario_claro
    )
    bs3 = ft.AlertDialog(
        modal=True,
        title=ft.Text("Selecciona la ranura de memoria", color=color_terciario_oscuro, weight=ft.FontWeight.W_500),
        content=ft.TextField(value="",label="Ranura (1-3)",label_style=ft.TextStyle(color=color_oscuro, weight=ft.FontWeight.W_500), color="BLACK", cursor_color="BLACK",border_color=color_oscuro, text_style=ft.TextStyle(weight=ft.FontWeight.W_500),width=10),
        actions=[
            ft.IconButton(icon=ft.icons.SAVE_ALT_ROUNDED, scale=1.5, on_click=save_chat,icon_color=color_oscuro),
            ft.IconButton(icon=ft.icons.CANCEL,scale=1.5, on_click=bs3_close, icon_color=color_oscuro),
        
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
        on_dismiss=bs_close,
        bgcolor=color_terciario_claro
    )



    # Añade los controles al diseño de la página
    page.overlay.append(bs3)
    page.overlay.append(bs2)
    page.overlay.append(bs)
    page.add(inicializador_de_interfaz_uno())

# Ejecuta la aplicación
ft.app(target=main)
