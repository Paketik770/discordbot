import discord
from discord import app_commands
from discord.ext import commands

import db


class RankModal(discord.ui.Modal, title="Новое звание"):
    rank_name = discord.ui.TextInput(
        label="Название звания",
        placeholder="Полковник, Сержант, Мастер клинка...",
        max_length=64,
        required=True,
    )

    reason = discord.ui.TextInput(
        label="За что / описание (необязательно)",
        placeholder="Например: за организацию мероприятия",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        db.add_rank(
            interaction.user.id,
            self.rank_name.value.strip(),
            self.reason.value.strip() if self.reason.value else "",
        )
        embed = discord.Embed(
            title="Звание установлено ✅",
            description=f"**{self.rank_name.value.strip()}**",
            color=discord.Color.green(),
        )
        if self.reason.value:
            embed.add_field(name="За что", value=self.reason.value, inline=False)
        embed.set_footer(text=f"Пользователь: {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)


class RankCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="звание", description="Заполнить форму на получение звания")
    async def rank(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RankModal())

    @app_commands.command(name="книжка", description="Показать наградную книжку (себе или другому игроку)")
    @app_commands.guild_only()
    async def book(
        self,
        interaction: discord.Interaction,
        участник: discord.Member = None,
    ):
        user = участник or interaction.user
        items = db.get_full_book(user.id)

        embed = discord.Embed(
            title=f"Наградная книжка — {user.display_name}",
            color=discord.Color.blue(),
        )
        embed.set_thumbnail(url=user.display_avatar.url)

        if not items:
            embed.description = "Пока пусто. 📭"
        else:
            lines = []
            for name, reason, awarded_at, kind in items:
                medal_icon = "🎖️" if kind == "Медаль" else "⭐"
                date = awarded_at[:10]
                text = f"{medal_icon} **{name}** · {date}"
                if reason:
                    text += f"\n   └ {reason}"
                lines.append(text)
            embed.description = "\n".join(lines)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(RankCommands(bot))