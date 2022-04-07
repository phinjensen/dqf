import { render } from "react-dom";
import React, { useState } from "react";

sentences = sentences.map((sentence) => {
  sentence.shuffled_entries = shuffleArray(
    Object.entries(sentence.translations)
  );
  return sentence;
});

function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

const storageKey = (sentenceIndex, translationKey) =>
  `${new URLSearchParams(window.location.search).get(
    "key"
  )}:${sentenceIndex}:${translationKey}`;

function Body() {
  const [index, setIndex] = useState(0);
  const [results, setResults] = useState(
    sentences.map((sentence, i) => {
      return Object.fromEntries(
        Object.entries(sentence.translations).map(([key, _]) => [
          key,
          window.localStorage.getItem(storageKey(i, key)) || "",
        ])
      );
    })
  );
  const sentence = sentences[index];
  const num_translations = Object.keys(sentence.translations).length;
  const incomplete = sentences.reduce((result, _, i) => {
    if (
      !Object.values(results[i]).every(
        (value) => value > 0 && value <= num_translations
      )
    ) {
      result.push(i + 1);
    }
    return result;
  }, []);
  return (
    <div className="content">
      <h1>Quality Assessment</h1>
      <div>
        <p>
          The following sentence has been translated {num_translations} times.
          Please read the sentence and its translations and then rank them from
          1 to {num_translations}, where 1 is the best and {num_translations} is
          the worst. If two translations are equivalent, feel free to put the
          same number for both.
        </p>
        <blockquote>{sentence.source}</blockquote>
        {sentence.shuffled_entries.map(([key, val]) => (
          <div key={`${index}-${key}`} className="row">
            <input
              placeholder="0"
              className="rank"
              type="number"
              value={results[index][key]}
              onChange={(event) => {
                event.preventDefault();
                let rank = event.target.valueAsNumber;
                if (isNaN(rank)) {
                  console.log("nan");
                  rank = "";
                } else if (rank < 1 || rank > num_translations) {
                  console.log("oogabooga");
                  rank = results[index][key];
                }
                results[index][key] = rank;
                setResults([...results]);
                window.localStorage.setItem(storageKey(index, key), rank);
              }}
            />
            <div className="sentence">{val}</div>
          </div>
        ))}
        <div className="dqf-nav">
          <button disabled={index === 0} onClick={() => setIndex(index - 1)}>
            Previous
          </button>
          <span>
            Sentence {index + 1} of {sentences.length}
          </span>
          {index === sentences.length - 1 ? (
            <button
              disabled={incomplete.length}
              onClick={() => {
                fetch("", {
                  method: "POST",
                  body: JSON.stringify(
                    results.map((result, i) => ({
                      id: sentences[i].id,
                      result,
                    }))
                  ),
                  headers: {
                    "Content-Type": "application/json",
                  },
                }).then((response) => console.log(response));
              }}
            >
              Submit Assessment
            </button>
          ) : (
            <button onClick={() => setIndex(index + 1)}>Next</button>
          )}
        </div>
        <div>
          <table id="summary">
            <thead>
              <tr>
                <th>Sentence</th>
                <th>Complete</th>
              </tr>
            </thead>
            <tbody>
              {sentences.map((_, i) => (
                <tr key={i}>
                  <td>
                    <a href="#" onClick={() => setIndex(i)}>
                      {i + 1}
                    </a>
                  </td>
                  <td>{incomplete.includes(i + 1) ? "❌" : "✅"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

const App = <Body />;

// Inject our app into the DOM
render(App, document.querySelector("#root"));
