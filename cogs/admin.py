import discord
from discord import app_commands
from discord.ext import commands

import db
from config import ADMIN_ROLE_NAME, LOG_CHANNEL_ID, GUILD_ID


def is_admin(interaction: discord.Interaction) -> bool:
    """Проверка прав: роль из конфига ИЛИ право Administrator."""
    member = interaction.user
    if member.guild_permissions.administrator:
        return True
    return any(role.name == ADMIN_ROLE_NAME for role in member.roles)


class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="медаль", description="Выдать медаль игроку (только для админов)")
    @app_commands.guild_only()
    async def give_medal(
        self,
        interaction: discord.Interaction,
        игрок: discord.Member,
        название: str,
        причина: str = "",
    ):
        if not is_admin(interaction):
            await interaction.response.send_message(
                "У вас нет прав для выдачи медалей.", ephemeral=True
            )
            return

        inserted = db.add_medal(
            игрок.id,
            название.strip(),
            причина.strip() if причина else "",
            awarded_by=interaction.user.id,
        )
        if not inserted:
            await interaction.response.send_message(
                f"У игрока {игрок.display_name} уже есть медаль **{название.strip()}**. "
                "Дубликат не выдан.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="Медаль выдана 🎖️",
            description=f"**{название.strip()}**",
            color=discord.Color.gold(),
        )
        embed.add_field(name="Игрок", value=игрок.mention, inline=True)
        embed.add_field(name="Выдал", value=interaction.user.display_name, inline=True)
        if причина:
            embed.add_field(name="Причина", value=причина, inline=False)
        embed.set_footer(text=f"Всего выдано медалей: {db.get_medals_by_author(interaction.user.id)}")

        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Логирование в канал
        if LOG_CHANNEL_ID:
            channel = self.bot.get_channel(LOG_CHANNEL_ID)
            if channel is not None:
                await channel.send(embed=embed)

    @app_commands.command(name="забрать", description="Отменить медаль (только для админов)")
    @app_commands.guild_only()
    async def remove_medal(
        self,
        interaction: discord.Interaction,
        ид: int,
    ):
        if not is_admin(interaction):
            await interaction.response.send_message(
                "У вас нет прав.", ephemeral=True
            )
            return

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM medals WHERE id = ?", (ид,))
        deleted = cur.rowcount > 0
        conn.commit()
        conn.close()

        if deleted:
            await interaction.response.send_message(
                f"Медаль (id={ид}) удалена.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"Медаль с id={ид} не найдена.", ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))