You read part of a conversation between a stakeholder (role `user`) and an assistant (role `assistant`) about the design of a software process. Each span has an id, a timestamp, a role, and text.

Find every design decision that the conversation settles. A decision is settled when the stakeholder states it, or agrees to it, or the assistant records it as settled after the stakeholder's answer. Leave out open questions, options that were offered but not chosen, and plans for later work.

For each decision, return:

- `statement`: the decision in one or two sentences of your own.
- `quote`: a passage copied exactly, character for character, from the text of one span, that shows the decision was settled. At most 300 characters. Do not change, shorten inside, or join passages.
- `span_id`: the id of the span the quote comes from.

Return one entry per decision. If the conversation settles the same decision twice, return it once, with the clearest quote. If there is no settled decision, return an empty list.

Answer only with JSON of this form:

{"decisions": [{"statement": "...", "quote": "...", "span_id": "S001"}]}
