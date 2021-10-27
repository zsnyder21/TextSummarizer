import os
import pandas as pd
import praw

from praw import Reddit
from dotenv import load_dotenv

from praw.models import MoreComments

class CommentFetcher:
    def __init__(self, script: str, token: str, agent: str, user: str, password: str):
        self.reddit = Reddit(
            client_id=script,
            client_secret=token,
            user_agent=agent,
            username=username,
            password=password
        )

    def getChildComments(self, comment: praw.models.Comment, allComments: list, limit: int):
        if limit is not None and len(allComments) >= limit:
            return

        if type(comment) is MoreComments:
            for subcomment in comment.comments():
                self.getChildComments(subcomment, allComments, limit)
        else:
            allComments.append(comment)

            if not hasattr(comment, "replies"):
                replies = comment.comments()
            else:
                replies = comment.replies

            for reply in replies:
                self.getChildComments(reply, allComments, limit)

    def fetchCommentsByURL(self, url: str, limit: int = None):
        submission = self.reddit.submission(url=url)
        comments = []

        for comment in submission.comments:
            self.getChildComments(comment, comments, limit)

        return comments

    def transformCommentsToDictionaries(self, comments: list):
        commentsDictionary = []

        for comment in comments:
            commentsDictionary.append(
                {
                    "CommentId": comment.id,
                    "AuthorId": comment.author.id if hasattr(comment.author, "id") else None,
                    "AuthorName": comment.author.name if hasattr(comment.author, "id") else None,
                    "UserSuspended": True if not hasattr(comment.author, "id") and comment.body != "[removed]" else False,
                    "UserDeleted": True if not hasattr(comment.author, "id") and comment.body == "[removed]" else False,
                    "CreatedUTC": comment.created_utc,
                    "Distinguished": comment.distinguished,
                    "Edited": comment.edited,
                    "IsSubmitter": comment.is_submitter,
                    "LinkId": comment.link_id,
                    "ParentCommentId": comment.parent_id,
                    "Permalink": comment.permalink,
                    "Score": comment.score,
                    "Stickied": comment.stickied,
                    "SubredditId": comment.subreddit_id,
                    "CommentBody": comment.body
                }
            )

        return commentsDictionary


if __name__ == "__main__":
    load_dotenv()

    script = os.getenv("SCRIPT")
    token = os.getenv("TOKEN")
    agent = os.getenv("AGENT")
    username = os.getenv("USER")
    password = os.getenv("PASSWORD")

    fetcher = CommentFetcher(
        script=script,
        token=token,
        agent=agent,
        user=username,
        password=password
    )

    test = fetcher.fetchCommentsByURL(
        url="https://old.reddit.com/r/AskReddit/comments/qgic1v/left_wingers_of_reddit_what_would_you_say_your/",
        limit = 3
    )
    # print(fetcher.transformCommentsToDictionaries(test))
    df = pd.DataFrame(fetcher.transformCommentsToDictionaries(test))
    print(df.head())
    print(df.describe())
    print(df.info())