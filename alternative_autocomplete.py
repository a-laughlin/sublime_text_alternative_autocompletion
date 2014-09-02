import sublime, sublime_plugin, re

class Candidate:
  def __init__(self, distance, text):
    self.distance = distance
    self.text = text

class AlternativeAutocompleteCommand(sublime_plugin.TextCommand):
  candidates = []
  previous_completion = None

  def run(self, edit, cycle = 'next'):
    self.edit = edit
    viewText = self.view.substr(sublime.Region(0, self.view.size()))
    for view in sublime.active_window().views():
      if view.id != self.view.id:
        viewText += view.substr( sublime.Region(0,view.size()) )
    self.insert_completion(self.view.sel()[0].b, viewText , cycle)

  def insert_completion(self, position, text, cycle):
    prefix_match = re.search(r'([a-zA-Z0-9$_\-]+)\Z', text[0:position], re.M | re.U)
    if prefix_match:
      prefix = prefix_match.group(1)

      if (self.previous_completion is None) or (prefix != self.previous_completion) or (prefix not in self.candidates):
        self.previous_completion = None
        self.candidates = self.find_candidates(prefix, position, text)
        self.candidates.append(prefix)

      if self.candidates:
        self.view.erase(self.edit, sublime.Region(prefix_match.start(1), prefix_match.end(1)))
        if self.previous_completion is None:
          completion = self.candidates[0]
        else:
          direction = 1 if cycle == 'next' else -1
          completion = self.candidates[(self.candidates.index(self.previous_completion) + direction) % len(self.candidates)]

        self.view.insert(self.edit, prefix_match.start(1), completion)
        self.previous_completion = completion

  def find_candidates(self, prefix, position, text):
    candidates = []
    fullTextRegex = re.compile(r'[^a-zA-Z0-9$_\-](' + re.escape(prefix) + r'[a-zA-Z0-9$_\-]+)', re.M | re.U)

    for match in fullTextRegex.finditer(text):
      candidates.append(Candidate(abs(match.start(1) - position), match.group(1)))
      if len(candidates) > 100:
        break
    if candidates:
      candidates.sort(key = lambda c: c.distance)
      candidates = [candidate.text for candidate in candidates]

    seen = set()
    return [value for value in candidates if value not in seen and not seen.add(value)]
