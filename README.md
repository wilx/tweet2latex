PyPi project: https://pypi.org/project/tweet2latex/

This is proof of concept utility for retrieval of Tweets by their IDs and
their conversion to LaTeX. This utility requires Python and
[`twarc`](https://github.com/edsu/twarc) module.

Run this from command line, e.g., like this:

    ./tweet2latex.py 762602474293321728 |tee tweet.tex

The invocation above will download tweet's information as JSON and it will
cache the JSON and downloaded images in current directory to avoid access
rate limitations of Twitter API should this tool be invoked several times in
succession.

The contents of the `tweet.tex` might looks something like this:

```latex
\begin{tweet}\tweetUserImage{https://pbs.twimg.com/profile\_images/887781725249585152/ihwPKKHi\_bigger.jpg}{ihwPKKHi-bigger.jpg}{701158958}\tweetUserName{701158958}{MedicNow}{MedicNow}\tweetUserEnd{}It could be worse. You could be the lifeguard at the \tweetHashtag{Rio}{\#Rio} swimming pool.... \tweetHashtag{MondayMotivation}{\#MondayMotivation} \tweetPhoto{https://twitter.com/MedicNow/status/762602474293321728/photo/1}{https://pbs.twimg.com/media/CpVOzW7WEAAhMte.jpg}{CpVOzW7WEAAhMte.jpg}{https://t.co/AfoOoV9qQw}\tweetRetweets{7}\tweetFavorites{12}\tweetItself{762602474293321728}{Mon Aug 08 10:52:52 +0000 2016}{August 8, 2016}{12:52:52 PM GMT+2}\end{tweet}
```


Then import the resulting `tweet.tex` in your LaTeX document:

```latex
\import{tweet}
```

Formatting of the tweet is up to you. See `tweet-document.tex` for example
usage. The following shows simple formatting for tweets:

```latex
\newenvironment{tweet}{%
  \newcommand{\tweetUserImage}[3]{%
    \begingroup%
      \includegraphics[keepaspectratio,height=1em]{##2}%
      \quad
    \endgroup
  }%
  \newcommand{\tweetUserName}[3]{\href{https://twitter.com/intent/user?user_id=##1}{##2}\quad
    \href{https://twitter.com/intent/user?user_id=##1}{{\small
        \color{gray}@##3}}}%
  \newcommand{\tweetUserVerified}{\hskip 0.16667em\relax{\small
      \color{cyan}\textcircled{\(\checkmark\)}}}%
  \newcommand{\tweetUserEnd}{\\}%
  \newcommand{\tweetHashtag}[2]{\href{https://twitter.com/hashtag/##1}{##2}}%
  \newcommand{\tweetUserMention}[2]{\href{https://twitter.com/intent/user?user_id=##1}{##2}}%
  \newcommand{\tweetUrl}[4]{\href{##2}{##3}}%
  \newcommand{\tweetInReplyToTweet}[3]{{\small \color{gray}in reply to
      \href{https://twitter.com/statuses/##1}{tweet} by
      \href{https://twitter.com/intent/user?user_id=##2}{@##3}}\\}%
  \newcommand{\tweetPhoto}[4]{\\\includegraphics[keepaspectratio]{##3}\\}%
  \newcommand{\tweetRetweets}[1]{\flushright{\small \(\color{gray}\circlearrowright\)\color{gray}\hskip 0.16667em\relax##1}}%
  \newcommand{\tweetFavorites}[1]{ {\small \(\color{gray}\heartsuit\)\color{gray}\hskip 0.16667em\relax##1}}%
  \newcommand{\tweetItself}[4]{%
    \quad\href{https://twitter.com/statuses/##1}{{\small \color{gray}##3 ##4}}}%
  \newcommand{\tweetPlace}[3]{\flushright {\small \color{gray}\href{##3}{##1, ##2}}}%
  \newfontfamily\emojifont{Symbola}[Scale=MatchUppercase]%
  \begin{tcolorbox}[size=small,enhanced,breakable,autoparskip,halign=flush left]%
    \sffamily%
}{\end{tcolorbox}}
```

The `tweet2latex.py` utility also downloads user image and linked images and
puts them in the working directory so that resulting document can use them.

