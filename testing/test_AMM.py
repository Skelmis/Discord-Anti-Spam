import unittest

from antispam.plugins import AntiMassMention
from testing.mocks.MockChannel import MockedChannel
from testing.mocks.MockMember import MockedMember
from testing.mocks.MockMessage import MockedMessage


class TestAMM(unittest.IsolatedAsyncioTestCase):
    async def test_message_mentions(self):
        member = MockedMember(name="bot", member_id=98987, mock_type="bot").to_mock()
        anti = AntiMassMention(member)

        x = None
        for i in range(5):
            m = MockedMessage(
                message_id=i,
                author_id=0,
                guild_id=3,
                message_mentions=["<@218180379088125955>"],
            ).to_mock()
            m.channel = MockedChannel(channel_id=2).to_mock()
            x = await anti.propagate(m)

        self.assertEqual(x["action"], "No action taken")


if __name__ == "__main__":
    unittest.main()
