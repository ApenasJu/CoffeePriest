import logging
import sqlite3
import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- Setup logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

DB_PATH = "coffee_bot.db"

# --- Database Helpers ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS configs (
        group_id TEXT PRIMARY KEY,
        members TEXT,
        ordem TEXT,
        periodo TEXT DEFAULT 'semanal',
        vezes_por_dia INTEGER DEFAULT 2
    )''')
    conn.commit()
    conn.close()


async def save_config(group_id, field, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f'''
        INSERT INTO configs (group_id, {field})
        VALUES (?, ?)
        ON CONFLICT(group_id) DO UPDATE SET {field} = ?
    ''', (group_id, json.dumps(value), json.dumps(value)))
    conn.commit()
    conn.close()


# --- Bot Command Handlers ---
async def membros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = str(update.effective_chat.id)
    if not context.args:
        await update.message.reply_text("⚠️ Use: /membros nome1, nome2, nome3")
        return
    members = [name.strip() for name in ' '.join(context.args).split(',') if name.strip()]
    if not members:
        await update.message.reply_text("⚠️ Nenhum membro válido encontrado.")
        return
    await save_config(group_id, "members", members)
    await save_config(group_id, "ordem", members)
    await update.message.reply_text("✅ Membros atualizados com sucesso!")


async def periodo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = str(update.effective_chat.id)
    if not context.args or context.args[0].lower() not in ['semanal', 'quinzenal', 'mensal']:
        await update.message.reply_text("⚠️ Use: /periodo semanal | quinzenal | mensal")
        return
    await save_config(group_id, "periodo", context.args[0].lower())
    await update.message.reply_text("✅ Período atualizado!")


async def vezesdia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = str(update.effective_chat.id)
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("⚠️ Use: /vezesdia <número>")
        return
    vezes = int(context.args[0])
    await save_config(group_id, "vezes_por_dia", vezes)
    await update.message.reply_text(f"✅ Vezes por dia atualizado para {vezes}!")


async def ajustar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = str(update.effective_chat.id)
    if not context.args:
        await update.message.reply_text("⚠️ Use: /ajustar nome1, nome2...")
        return
    ordem = [name.strip() for name in ' '.join(context.args).split(',') if name.strip()]
    await save_config(group_id, "ordem", ordem)
    await update.message.reply_text("✅ Ordem ajustada!")


# --- Setup Bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot de Café pronto! Use /membros para começar.")


def main():
    init_db()
    TOKEN = os.getenv("7751557507:AAEUGfRV0gTSq-CySLrfIbrLLR1BNL5WjW4")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("membros", membros))
    app.add_handler(CommandHandler("periodo", periodo))
    app.add_handler(CommandHandler("vezesdia", vezesdia))
    app.add_handler(CommandHandler("ajustar", ajustar))

    print("☕ Bot está rodando...")
    app.run_polling()


if __name__ == '__main__':
    main()
