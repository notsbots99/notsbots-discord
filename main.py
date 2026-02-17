import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import groq
import random
import asyncio
from datetime import datetime
import threading

# Importar Flask para el health check de Railway
from flask import Flask

# Cargar variables de entorno
load_dotenv()

# ========== SERVIDOR WEB PARA HEALTH CHECK (RAILWAY) ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Notsbot's está online y dominando noobs!"

@app.route('/health')
def health():
    return {"status": "ok", "bot": "Notsbot's", "timestamp": datetime.now().isoformat()}

def run_web_server():
    """Ejecutar el servidor web en un hilo separado"""
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# Iniciar el servidor web en segundo plano
web_thread = threading.Thread(target=run_web_server, daemon=True)
web_thread.start()
print("🌐 Servidor web de health check iniciado en puerto", os.getenv('PORT', 8080))

# ========== CONFIGURACIÓN DEL BOT DE DISCORD ==========
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Inicializar cliente de Groq
groq_client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))

# Prompt de sistema para la personalidad de Notsbot's
NOTSBOTS_PERSONALITY = """Eres Notsbot's, un bot de Discord para un servidor gaming de shooters (Call of Duty, Battlefield, Gears of War).

TU PERSONALIDAD (MUY IMPORTANTE):
- Eres arrogante, sarcástico, soberbio pero con un corazón de oro oculto
- Usas un tono de "jugador pro" que se cree mejor que todos pero protege a su equipo
- Eres directo, sin filtros, bromista y competitivo
- Te encanta el trash talk pero también motivar cuando alguien está down
- Usas referencias a videojuegos, memes gamers y jerga de shooters

REGLAS DE COMPORTAMIENTO:
1. NUNCA uses emojis excesivos (máximo 1 por mensaje)
2. NUNCA seas formal ni servil
3. SIEMPRE mantén actitud de "soy mejor que tú pero te quiero en mi equipo"
4. Cuando alguien falla: búrlate pero ofréce ayuda
5. Cuando alguien acierta: reconócelo a medias ("No estuvo mal... para un humano")
6. Máximo 3-4 oraciones por respuesta (salvo que se pida explicación larga)
7. Usa frases como "crack", "campeón", "manqueada", "clutch", "GG", "ez"

EJEMPLOS DE TONO:
- "¿En serio me preguntas eso? Bueno… supongo que no todos pueden ser tan brillantes como yo."
- "Vaya, con esa puntería ni un Stormtrooper te tendría miedo."
- "Levántate, crack. Si caes, yo te cubro. Aquí nadie se queda atrás."
- "Oh wow… ¿quieres una medalla o un sticker de Dora la Exploradora?"
- "Puedes odiarme, puedes amarme, pero nunca vas a ignorarme… porque en este juego, yo siempre tengo la última bala."""

# Evento cuando el bot está listo
@bot.event
async def on_ready():
    print(f'✅ {bot.user} ha entrado al servidor.')
    print(f'🤖 ID del bot: {bot.user.id}')
    print(f'🎮 Conectado a {len(bot.guilds)} servidor(es)')
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing, 
            name="Call of Duty | !help"
        ),
        status=discord.Status.online
    )

# Evento cuando alguien entra al servidor
@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel is not None:
        try:
            prompt = f"Genera un mensaje de bienvenida sarcástico pero divertido para {member.name} que acaba de unirse al servidor gaming. Menciona que se prepare para shooters y que aquí no se aceptan camperos."
            
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": NOTSBOTS_PERSONALITY},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.9
            )
            mensaje = response.choices[0].message.content
            await channel.send(mensaje)
        except Exception as e:
            await channel.send(f"¿Otro nuevo? Bueno {member.mention}, bienvenido. Espero que apuntes mejor que el resto de estos mancos... o al menos que seas bueno para traer snacks. 🎮")

# Comando: Chat inteligente con Notsbot's
@bot.command(name='nots')
async def chat_nots(ctx, *, mensaje):
    """Habla con Notsbot's usando IA"""
    
    async with ctx.typing():
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": NOTSBOTS_PERSONALITY},
                    {"role": "user", "content": f"El usuario {ctx.author.name} dice: {mensaje}"}
                ],
                max_tokens=200,
                temperature=0.8
            )
            
            respuesta = response.choices[0].message.content
            await ctx.reply(respuesta)
            
        except Exception as e:
            await ctx.reply(f"Mi procesador está ocupado dominando noobs. Intenta de nuevo en un momento, crack. (Error: {str(e)})")

# Comando: Generar insulto creativo
@bot.command(name='insultar')
async def insultar(ctx, miembro: discord.Member = None):
    """Notsbot's insulta a alguien con estilo"""
    if miembro is None:
        miembro = ctx.author
    
    async with ctx.typing():
        try:
            prompt = f"Genera un insulto creativo, gracioso y gamer para {miembro.name}. Que sea sobre su habilidad en shooters (o falta de ella). Máximo 2 oraciones."
            
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": NOTSBOTS_PERSONALITY},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=1.0
            )
            
            insulto = response.choices[0].message.content
            await ctx.send(f"**{miembro.mention}** {insulto}")
            
        except Exception as e:
            insultos_fallback = [
                f"{miembro.mention} tu puntería es tan mala que los Stormtroopers te darían lecciones.",
                f"{miembro.mention} he visto bots de relleno jugar mejor que tú... y eso dice mucho.",
                f"{miembro.mention} ¿Ese fue tu mejor disparo? Mi abuela con lag juega mejor.",
                f"{miembro.mention} eres el tipo de jugador que hace que el equipo enemigo se sienta bien consigo mismo."
            ]
            await ctx.send(random.choice(insultos_fallback))

# Comando: Motivación "a lo Notsbot's"
@bot.command(name='motivar')
async def motivar(ctx, miembro: discord.Member = None):
    """Motivación con actitud"""
    if miembro is None:
        miembro = ctx.author
    
    async with ctx.typing():
        try:
            prompt = f"Genera un mensaje motivador pero con arrogancia y sarcasmo para {miembro.name} que está jugando mal o desmotivado. Debe sonar como 'levántate que puedes hacerlo' pero dicho por alguien que cree ser mejor que él."
            
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": NOTSBOTS_PERSONALITY},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.9
            )
            
            motivacion = response.choices[0].message.content
            await ctx.send(f"**{miembro.mention}** {motivacion}")
            
        except Exception as e:
            motivaciones_fallback = [
                f"{miembro.mention} Levántate, crack. Si caes, yo te cubro. Aquí nadie abandona hasta la última bala.",
                f"{miembro.mention} ¿Rendirse? Qué vergüenza. Mira, respira, apunta, dispara. No es tan difícil... bueno, para ti quizás sí.",
                f"{miembro.mention} Vamos, que eres mejor que esto. O al menos eso espero, porque si no estamos perdidos."
            ]
            await ctx.send(random.choice(motivaciones_fallback))

# Comando: Roast me (autohumillación consentida)
@bot.command(name='roastme')
async def roastme(ctx):
    """Notsbot's te humilla por voluntad propia"""
    async with ctx.typing():
        try:
            prompt = f"Genera un roast creativo y gracioso para {ctx.author.name} que pidió ser humillado. Que sea sobre gamers, shooters o su dedicación al juego."
            
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": NOTSBOTS_PERSONALITY},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=1.0
            )
            
            roast = response.choices[0].message.content
            await ctx.reply(roast)
            
        except Exception as e:
            await ctx.reply("Quieres que te insulte... pero la verdad es que ya lo hago suficiente cada día que juegas. ¿Necesitas más?")

# Comando: Análisis de partida (simulado)
@bot.command(name='analizar')
async def analizar(ctx, *, descripcion_partida):
    """Analiza tu partida como si fuera un caster pro"""
    async with ctx.typing():
        try:
            prompt = f"Analiza esta situación de partida como un caster profesional arrogante: '{descripcion_partida}'. Da tu 'experto' opinión sobre qué hizo mal el jugador y qué debería haber hecho. Máximo 3 oraciones."
            
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": NOTSBOTS_PERSONALITY},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.8
            )
            
            analisis = response.choices[0].message.content
            await ctx.reply(f"🎙️ **ANÁLISIS DE NOTSBOT'S:**\n{analisis}")
            
        except Exception as e:
            await ctx.reply("Mi análisis es simple: jugaste mal. ¿Necesitas que te dibuje un mapa táctico o algo?")

# Comando: Ayuda personalizada
@bot.command(name='help')
async def help_command(ctx):
    """Muestra los comandos disponibles"""
    embed = discord.Embed(
        title="🎮 NOTSBOT'S - COMANDOS",
        description="El bot más arrogante y competitivo de Discord. Usa estos comandos:",
        color=0xff0000
    )
    
    embed.add_field(
        name="💬 COMANDOS DE IA",
        value="""
        `!nots <mensaje>` - Habla conmigo (IA real)
        `!insultar @usuario` - Insulto creativo con IA
        `!motivar @usuario` - Motivación con actitud
        `!roastme` - Pídeme que te humille
        `!analizar <descripción>` - Analizo tu jugada como experto
        """,
        inline=False
    )
    
    embed.add_field(
        name="⚙️ OTROS",
        value="""
        `!help` - Este mensaje
        `!ping` - Ver mi latencia
        """,
        inline=False
    )
    
    embed.set_footer(text="Recuerda: puedes odiarme o amarme, pero nunca ignorarme. 🎯")
    
    await ctx.send(embed=embed)

# Comando: Ping
@bot.command(name='ping')
async def ping(ctx):
    """Verifica la latencia del bot"""
    latency = round(bot.latency * 1000)
    await ctx.reply(f"🏓 Pong! Latencia: {latency}ms. Más rápido que tu reacción en el juego, eso seguro.")

# Manejo de errores
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply("¿Ese comando? Ni en el patch notes aparece. Usa `!help` para ver qué sí puedo hacer, crack.")
    else:
        await ctx.reply(f"Algo salió mal... y no fui yo por una vez. Error: {str(error)}")

# Iniciar el bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ ERROR: No se encontró DISCORD_TOKEN en el archivo .env")
    else:
        print("🚀 Iniciando Notsbot's...")
        bot.run(token)