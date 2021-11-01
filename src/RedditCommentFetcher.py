import os
import pandas as pd
import praw

from praw import Reddit
from dotenv import load_dotenv

from praw.models import MoreComments

class CommentFetcher:
    """
    Fetch comments from reddit

    """
    def __init__(self, script: str, token: str, agent: str, user: str, password: str) -> None:
        """
        Set required properties

        :param script: Client Id
        :param token: Client Secret
        :param agent: User Agent
        :param user: Username
        :param password: Password
        :returns None
        """
        self.reddit = Reddit(
            client_id=script,
            client_secret=token,
            user_agent=agent,
            username=user,
            password=password
        )

    def getChildComments(self, comment: praw.models.Comment, allComments: list, limit: int) -> None:
        """
        Fetch child comments from a given comment object

        :param comment: Comment object to fetch child comments from
        :param allComments: List holding all comments
        :param limit: Maximum number of comments to be fetching
        :return: None
        """
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

    def fetchCommentsBySubmission(self, submission: praw.models.Submission, limit: int = None) -> list:
        """
        Fetch comments on a given submission

        :param submission: Submission to fetch comments from (Submission object or URL)
        :param limit: Maximum number of comments to fetch
        :return: List of comments
        """
        if type(submission) is str:
            submission = self.reddit.submission(url=url)

        comments = []

        for comment in submission.comments:
            self.getChildComments(comment, comments, limit)

        return comments

    def fetchSubmissionComments(self, submission: praw.models.Submission, limit: int = None) -> list:
        """
        DEPRECATED! Grabs all comments. Deprecated because no control of limitations

        :param submission: Submission to fetch comments from
        :param limit: Number of MoreComments instances to resolve
        :return: List of comments
        """
        comments = submission.comments
        comments.replace_more(limit=limit)

        return pd.DataFrame(self.transformCommentsToDictionaries(comments.list()))

    def fetchSubmissions(self, subreddit: str) -> praw.models.ListingGenerator:
        """
        Fetch top (all-time) submissions from a given subreddit

        :param subreddit: Subreddit name
        :return: Top all=time submissions from a subreddit
        """
        submissions = self.reddit.subreddit(subreddit).top("all")

        return submissions

    def fetchSubredditComments(self,
                               subreddit: str,
                               submissionLimit: int = 1000,
                               commentsPerSubmission: int = 5000,
                               save: bool = False,
                               saveLocation: str = "../data/comments.pkl",
                               offset: int = 0) -> pd.DataFrame:
        """
        Fetch comments from a given subreddit

        :param subreddit: Name of subreddit to fetch comments from
        :param submissionLimit: Maximum number of submissions to fetch comments from
        :param commentsPerSubmission: Number of comments to fetch per submission
        :param save: Whether or not to save the data
        :param saveLocation: Where to save the data
        :param How many submissions to skip
        :return: Dataframe containing the comments
        """
        if os.path.exists(saveLocation):
            data = pd.read_pickle(saveLocation)
        else:
            data = None

        submissions = self.fetchSubmissions(subreddit)
        submissionCount = 1

        for submission in submissions:
            submissionCount += 1

            # Skip the required number of submissions
            if submissionCount <= offset:
                continue

            comments = self.fetchCommentsBySubmission(submission, limit=commentsPerSubmission)

            # First pass - create dataframe
            if data is None:
                data = pd.DataFrame(self.transformCommentsToDictionaries(comments, submission))
            else:
                # Subsequent passes - append new data
                data = data.append(pd.DataFrame(self.transformCommentsToDictionaries(comments, submission)))

            # Checkpoint the data
            if save:
                data.to_pickle(saveLocation)

            if submissionCount > submissionLimit:
                break

        return data

    def transformCommentsToDictionaries(self, comments: list, submission: praw.models.Submission) -> list:
        """
        Converts a list of comment objects to a list of dictionaries
        containing the relevant key/value pairs

        :param comments: List of comment objects to convert
        :param submission: Submission object from which the comment originated
        :return: List of dictionaries
        """
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
                    "CommentScore": comment.score,
                    "Stickied": comment.stickied,
                    "SubmissionId": submission.id,
                    "UpvoteRatio": submission.upvote_ratio,
                    "SubmissionScore": submission.score,
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

    df = fetcher.fetchSubredditComments(
        subreddit="AskReddit",
        submissionLimit=2500,
        commentsPerSubmission=20000,
        save=True,
        saveLocation="../data/comments.pkl",
        offset=8
    )