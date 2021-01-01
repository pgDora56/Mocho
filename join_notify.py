import asyncio


class JoinNotify:
    def __init__(self, watch_category, notify_ch):
        self.watch_category = watch_category
        self.notify_ch = notify_ch

    async def check(self, member, befch, aftch):
        msg = None
        if befch is None:
            if aftch.category_id == self.watch_category:
                msg = await self.notify_ch.send(
                    f"{member.display_name}が `{aftch}` に入室したよ(o・∇・o)")
        elif aftch is None:
            if befch.category_id == self.watch_category:
                msg = await self.notify_ch.send(
                    f"{member.display_name}が `{befch}` から退出したよ(o・∇・o)")
        elif befch != aftch:
            if befch.category_id == self.watch_category or \
                    aftch.category_id == self.watch_category:
                msg = await self.notify_ch.send(
                    f"{member.display_name}が "
                    "`{befch}` から `{aftch}` に移動したよ(o・∇・o)")
        if msg is None:
            return

        await asyncio.sleep(180)
        await msg.delete()
