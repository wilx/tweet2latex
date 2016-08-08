This is proof of concept utility for retrieval of Tweets by their IDs and
their conversion to LaTeX. This utility requires Python and
[`twarc`](https://github.com/edsu/twarc) module.

Run this from command line, e.g., like this:

    ./tweet2latex.py 762602474293321728 |tee tweet.tex

The contents of the `tweet.tex` might looks something like this:

```latex
\begin{tweet}\tweetUserImage{https://pbs.twimg.com/profile\_images/683232086958993408/rnyugqzL\_normal.jpg}{rnyugqzL-normal.jpg}{701158958}\tweetUserName{701158958}{MedicNow}It could be worse. You could be the lifeguard at the \tweetHashtag{Rio}{\#Rio} swimming pool.... \tweetHashtag{MondayMotivation}{\#MondayMotivation} \tweetPhoto{http://twitter.com/MedicNow/status/762602474293321728/photo/1}{https://pbs.twimg.com/media/CpVOzW7WEAAhMte.jpg}{CpVOzW7WEAAhMte.jpg}{https://t.co/AfoOoV9qQw}\tweetItself{762602474293321728}{Mon Aug 08 10:52:52 +0000 2016}\end{tweet}
```


Then import the resulting `tweet.tex` in your LaTeX document:

```latex
\import{tweet}
```

Formatting of the tweet is up to you. See `tweet-document.tex` for example usage. The following shows simple formatting for tweets::

```latex
\newenvironment{tweet}{%
  \newcommand{\tweetUserImage}[3]{%
    \begingroup%
      \includegraphics[keepaspectratio,height=1em]{##2}%
      \quad
    \endgroup
  }%
  \newcommand{\tweetUserName}[2]{\href{https://twitter.com/intent/user?user_id=##1}{##2}\\}%
  \newcommand{\tweetHashtag}[2]{\href{https://twitter.com/hashtag/##1}{##2}}%
  \newcommand{\tweetUserMention}[2]{\href{https://twitter.com/intent/user?user_id=##1}{##2}}%
  \newcommand{\tweetUrl}[4]{\href{##2}{##3}}%
  \newcommand{\tweetPhoto}[3]{\\\includegraphics[keepaspectratio]{##3}\\}%
  \newcommand{\tweetItself}[2]{\flushright \href{https://twitter.com/statuses/##1}{##2}}%
  \begin{tcolorbox}[size=small,nobeforeafter]%
  \RaggedRight%
}{\end{tcolorbox}}

```

The `tweet2latex.py` utility also downloads user image and linked images and
puts them in the working directory so that resulting document can use them.

