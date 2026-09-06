class KnowledgeBase:
    """Store facts and Horn-clause rules and infer conclusions by forward chaining."""

    def __init__(self):
        self.facts = set()
        self.rules = []

    def tell_fact(self, fact_string):
        """Add a fact to the knowledge base."""
        self.facts.add(fact_string)

    def tell_rule(self, premise_list, conclusion_string):
        """Add a Horn-clause rule to the knowledge base."""
        self.rules.append((list(premise_list), conclusion_string))

    def clear_facts(self):
        """Forget current percept facts while keeping the domain rules."""
        self.facts.clear()

    def forward_chain(self):
        """Infer every conclusion that follows from the currently known facts."""
        new_facts_added = True

        while new_facts_added:
            new_facts_added = False

            for premises, conclusion in self.rules:
                if conclusion not in self.facts:
                    if all(premise in self.facts for premise in premises):
                        self.facts.add(conclusion)
                        new_facts_added = True
