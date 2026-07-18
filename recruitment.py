from __future__ import annotations

from dataclasses import dataclass, field

import discord


@dataclass
class Recruitment:

    # 募集メッセージ
    message: discord.Message

    # 定員
    limit: int

    # 募集チャンネル
    channel: discord.TextChannel

    # 募集が開いているか
    open: bool = True

    # 参加者
    participants: set[int] = field(default_factory=set)

    # -------------------------
    # 人数
    # -------------------------

    @property
    def count(self) -> int:
        return len(self.participants)

    # -------------------------
    # 参加
    # -------------------------

    def join(self, user_id: int) -> bool:

        if user_id in self.participants:
            return False

        self.participants.add(user_id)
        return True

    # -------------------------
    # 取消
    # -------------------------

    def drop(self, user_id: int) -> bool:

        if user_id not in self.participants:
            return False

        self.participants.remove(user_id)
        return True

    # -------------------------
    # メッセージ更新
    # -------------------------

    async def update(self):

        text = (
            "📢 **試合参加者募集中！**\n\n"
            f"現在の参加人数：**{self.count} / {self.limit}人**\n\n"
            "参加する人\n"
            "`/can`\n\n"
            "取り消す人\n"
            "`/drop`"
        )

        await self.message.edit(content=text)

    # -------------------------
    # 募集終了
    # -------------------------

    async def close(self, bot):

        self.open = False

        names = []

        for uid in self.participants:

            user = await bot.fetch_user(uid)
            names.append(user.display_name)

        if names:

            result = "\n".join(
                f"{i+1}. {name}"
                for i, name in enumerate(names)
            )

        else:

            result = "参加者はいませんでした。"

        await self.message.edit(
            content="✅ **募集終了**"
        )

        await self.channel.send(
            f"## 参加者一覧\n\n{result}"
        )
        