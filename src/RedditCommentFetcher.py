import os

from praw import Reddit
from dotenv import load_dotenv

class CommentFetcher:
    def __init__(self):
        load_dotenv()

        script = os.getenv("SCRIPT")
        token = os.getenv("TOKEN")
        agent = os.getenv("AGENT")
        username = os.getenv("USER")
        password = os.getenv("PASSWORD")

        self.reddit = Reddit(
            client_id=script,
            client_secret=token,
            user_agent=agent,
            username=username,
            password=password
        )

    def getChildComments(self, comment, allComments):
        allComments.append(comment)

        if not hasattr(comment, "replies"):
            replies = comment.comments()
        else:
            replies = comment.replies

        for reply in replies:
            self.getChildComments(reply, allComments)

    def fetchCommentsByURL(self, url: str):
        submission = self.reddit.submission(url=url)
        comments = []

        for comment in submission.comments:
            self.getChildComments(comment, comments)

        print(len(comments), "\r\n", [comment.body for comment in comments])


if __name__ == "__main__":
    fetcher = CommentFetcher()

    fetcher.fetchCommentsByURL(url="https://old.reddit.com/r/AskReddit/comments/qgfnsd/what_should_be_the_united_states_next/")