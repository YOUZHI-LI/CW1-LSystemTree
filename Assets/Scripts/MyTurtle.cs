using System.Collections.Generic;
using UnityEngine;

// One line drawn by the turtle.
public struct Segment
{
    public Vector3 start;
    public Vector3 end;
    public int depth;   // how many '[' deep the segment is (0 = trunk)
}

// Turtle interpretation of the string (ABOP section 1.5).
// The turtle starts at the origin facing up (+Y). Its orientation is a Quaternion,
// so the same code works for 2D and 3D L-systems.
//
//   F G   move forward and draw a line     f   move forward without drawing
//   + -   turn left / right                & ^ pitch down / up
//   \ /   roll left / right                |   turn around
//   [ ]   save / restore the turtle        other symbols (X, A, L ...) are ignored
public static class MyTurtle
{
    struct State
    {
        public Vector3 position;
        public Quaternion rotation;
        public float length;
        public int depth;
    }

    public static List<Segment> Draw(string symbols, float angle, float length, float lengthRatio)
    {
        List<Segment> segments = new List<Segment>();
        Stack<State> stack = new Stack<State>();

        State turtle = new State();
        turtle.position = Vector3.zero;
        turtle.rotation = Quaternion.identity;
        turtle.length = length;
        turtle.depth = 0;

        foreach (char c in symbols)
        {
            switch (c)
            {
                case 'F':
                case 'G':
                    // The heading is the turtle's local up axis.
                    Vector3 end = turtle.position + turtle.rotation * Vector3.up * turtle.length;
                    Segment s = new Segment();
                    s.start = turtle.position;
                    s.end = end;
                    s.depth = turtle.depth;
                    segments.Add(s);
                    turtle.position = end;
                    break;
                case 'f':
                    turtle.position += turtle.rotation * Vector3.up * turtle.length;
                    break;

                // Multiplying on the right rotates around the turtle's OWN axes.
                case '+': turtle.rotation *= Quaternion.Euler(0, 0, angle); break;    // turn left (around Z)
                case '-': turtle.rotation *= Quaternion.Euler(0, 0, -angle); break;   // turn right
                case '&': turtle.rotation *= Quaternion.Euler(angle, 0, 0); break;    // pitch down (around X)
                case '^': turtle.rotation *= Quaternion.Euler(-angle, 0, 0); break;   // pitch up
                case '\\': turtle.rotation *= Quaternion.Euler(0, angle, 0); break;   // roll left (around Y)
                case '/': turtle.rotation *= Quaternion.Euler(0, -angle, 0); break;   // roll right
                case '|': turtle.rotation *= Quaternion.Euler(0, 0, 180); break;      // turn around

                case '[':
                    // Remember where we are, then start a thinner, shorter branch.
                    stack.Push(turtle);
                    turtle.depth++;
                    turtle.length *= lengthRatio;
                    break;
                case ']':
                    // Go back to where the branch started.
                    if (stack.Count > 0) turtle = stack.Pop();
                    break;
            }
        }
        return segments;
    }
}
