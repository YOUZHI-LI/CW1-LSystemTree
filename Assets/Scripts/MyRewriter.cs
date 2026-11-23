using System.Collections.Generic;
using System.Text;

// One production rule, for example  F -> F[+F]F[-F]F
// If a symbol has more than one rule, the probability decides which one is used
// (this is a stochastic L-system, ABOP section 1.7).
[System.Serializable]
public class Rule
{
    public char symbol;
    public string successor;
    public float probability;

    public Rule(char symbol, string successor, float probability)
    {
        this.symbol = symbol;
        this.successor = successor;
        this.probability = probability;
    }
}

// Rewrites the axiom with the rules.
public static class MyRewriter
{
    // Every symbol of the string is replaced at the same time (parallel rewriting),
    // and this is repeated 'iterations' times.
    // Returns null if the string becomes longer than maxLength.
    public static string Generate(string axiom, List<Rule> rules, int iterations, int seed, int maxLength)
    {
        // The same seed always gives the same random choices, so a tree can be reproduced.
        System.Random random = new System.Random(seed);
        string current = axiom;

        for (int i = 0; i < iterations; i++)
        {
            // Read from 'current', write into 'next'. Symbols created in this
            // iteration are only rewritten in the next iteration.
            StringBuilder next = new StringBuilder();
            foreach (char c in current)
            {
                next.Append(Rewrite(c, rules, random));
            }

            if (next.Length > maxLength) return null;
            current = next.ToString();
        }
        return current;
    }

    // Returns what one symbol turns into. Symbols without a rule (+ - [ ] ...) stay the same.
    static string Rewrite(char c, List<Rule> rules, System.Random random)
    {
        // Find all rules for this symbol.
        List<Rule> matches = new List<Rule>();
        float total = 0f;
        foreach (Rule rule in rules)
        {
            if (rule.symbol == c)
            {
                matches.Add(rule);
                total += rule.probability;
            }
        }

        if (matches.Count == 0) return c.ToString();
        if (matches.Count == 1) return matches[0].successor;

        // Several rules: pick one with a chance proportional to its probability.
        float pick = (float)random.NextDouble() * total;
        foreach (Rule rule in matches)
        {
            pick -= rule.probability;
            if (pick <= 0f) return rule.successor;
        }
        return matches[matches.Count - 1].successor;
    }
}
