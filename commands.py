import discord

from discord import app_commands
from discord.ext import commands

from recruitment import Recruitment


class RecruitmentCommands(commands.Cog):

    def __init__(self, bot: commands.Bot):

        self.bot = bot

        # チャンネルID → Recruitment
        self.recruitments: dict[int, Recruitment] = {}

    # ------------------------
    # 募集開始
    # ------------------------

    @app_commands.command(
        name="open",
        description="募集を開始します"
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(limit="募集人数")
    async def open(
        self,
        interaction: discord.Interaction,
        limit: int
    ):

        channel_id = interaction.channel.id

        if channel_id in self.recruitments:

            await interaction.response.send_message(
                "このチャンネルでは既に募集しています。",
                ephemeral=True
            )

            return

        message = await interaction.channel.send(
            "募集を作成しています..."
        )

        recruit = Recruitment(
            message=message,
            limit=limit,
            channel=interaction.channel,
        )

        self.recruitments[channel_id] = recruit

        await recruit.update()

        await interaction.response.send_message(
            "募集を開始しました。",
            ephemeral=True
        )
    # ------------------------
    # 参加
    # ------------------------

    @app_commands.command(
        name="can",
        description="募集に参加します"
    )
    async def can(
        self,
        interaction: discord.Interaction
    ):

        recruit = self.get_recruitment(interaction.channel.id)

        if recruit is None:

            await interaction.response.send_message(
                "このチャンネルでは募集が行われていません。",
                ephemeral=True
            )

            return

        if not recruit.open:

            await interaction.response.send_message(
                "募集は終了しています。",
                ephemeral=True
            )

            return

        if not recruit.join(interaction.user.id):

            await interaction.response.send_message(
                "既に参加しています。",
                ephemeral=True
            )

            return

        await recruit.update()

        await interaction.response.send_message(
            "✅ 参加しました。",
            ephemeral=True
        )

    # ------------------------
    # 参加取消
    # ------------------------

    @app_commands.command(
        name="drop",
        description="参加を取り消します"
    )
    async def drop(
        self,
        interaction: discord.Interaction
    ):

        recruit = self.get_recruitment(interaction.channel.id)

        if recruit is None:

            await interaction.response.send_message(
                "このチャンネルでは募集が行われていません。",
                ephemeral=True
            )

            return

        if not recruit.open:

            await interaction.response.send_message(
                "募集は終了しています。",
                ephemeral=True
            )

            return

        if not recruit.drop(interaction.user.id):

            await interaction.response.send_message(
                "まだ参加していません。",
                ephemeral=True
            )

            return

        await recruit.update()

        await interaction.response.send_message(
            "❌ 参加を取り消しました。",
            ephemeral=True
        )
            # ------------------------
    # 現在の人数
    # ------------------------

    @app_commands.command(
        name="status",
        description="現在の参加人数を表示します"
    )
    async def status(
        self,
        interaction: discord.Interaction
    ):

        recruit = self.get_recruitment(interaction.channel.id)

        if recruit is None:

            await interaction.response.send_message(
                "このチャンネルでは募集が行われていません。",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            f"現在 **{recruit.count} / {recruit.limit}人** が参加しています。",
            ephemeral=True
        )

    # ------------------------
    # 参加者一覧（管理者のみ）
    # ------------------------

    @app_commands.command(
        name="list",
        description="参加者一覧を表示します"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def list_players(
        self,
        interaction: discord.Interaction
    ):

        recruit = self.get_recruitment(interaction.channel.id)

        if recruit is None:

            await interaction.response.send_message(
                "このチャンネルでは募集が行われていません。",
                ephemeral=True
            )

            return

        if recruit.count == 0:

            await interaction.response.send_message(
                "参加者はいません。",
                ephemeral=True
            )

            return

        names = []

        for user_id in recruit.participants:

            member = interaction.guild.get_member(user_id)

            if member is None:

                try:
                    member = await interaction.guild.fetch_member(user_id)
                except discord.NotFound:
                    continue

            names.append(member.display_name)

        text = "\n".join(
            f"{i + 1}. {name}"
            for i, name in enumerate(sorted(names))
        )

        await interaction.response.send_message(
            f"## 参加者一覧\n\n{text}",
            ephemeral=True
        )
            # ------------------------
    # 募集終了
    # ------------------------

    @app_commands.command(
        name="close",
        description="募集を終了します"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def close(
        self,
        interaction: discord.Interaction
    ):

        channel_id = interaction.channel.id

        recruit = self.get_recruitment(channel_id)

        if recruit is None:

            await interaction.response.send_message(
                "このチャンネルでは募集していません。",
                ephemeral=True
            )

            return

        await recruit.close(self.bot)

        del self.recruitments[channel_id]

        await interaction.response.send_message(
            "募集を終了しました。",
            ephemeral=True
        )
    # ------------------------
    # 取得
    # ------------------------

    def get_recruitment(
        self,
        channel_id: int
    ) -> Recruitment | None:

        return self.recruitments.get(channel_id)


async def setup(bot: commands.Bot):

    await bot.add_cog(
        RecruitmentCommands(bot)
    )