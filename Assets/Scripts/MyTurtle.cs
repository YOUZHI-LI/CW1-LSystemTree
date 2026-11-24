using System.Collections.Generic;
using UnityEngine;

public struct Segment
{
    public Vector3 start;
    public Vector3 end;
    public int depth;   
}


public struct Leaf
{
    public Vector3 position;
    public Quaternion rotation;
}


//   F G   move forward and draw a line     f   move forward without drawing
//   + -   turn left / right                & ^ pitch down / up
//   \ /   roll left / right                |   turn around
//   [ ]   save / restore the turtle        L   leaf (a leaf is also added at every ']')
//   other symbols gnored
public static class MyTurtle
{
    struct State
    {
        public Vector3 position;
        public Quaternion rotation;
        public float length;
        public int depth;
    }

    // Returns the lines; the leaf positions come back in "leaves".
    public static List<Segment> Draw(string symbols, float angle, float length, float lengthRatio, out List<Leaf> leaves)
    {
        List<Segment> segments = new List<Segment>();
        leaves = new List<Leaf>();
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
                    //create the line
                    Segment s = new Segment();
                    s.start = turtle.position;
                    s.end = end;
                    s.depth = turtle.depth;
                    segments.Add(s);
                    turtle.position = end;
                    break;
                case 'f':
                    //forward without drawing a line
                    turtle.position += turtle.rotation * Vector3.up * turtle.length;
                    break;

               
                case '+': turtle.rotation *= Quaternion.Euler(0, 0, angle); break;    // turn left (around Z)
                case '-': turtle.rotation *= Quaternion.Euler(0, 0, -angle); break;   // turn right
                case '&': turtle.rotation *= Quaternion.Euler(angle, 0, 0); break;    // pitch down (around X)
                case '^': turtle.rotation *= Quaternion.Euler(-angle, 0, 0); break;   // pitch up
                case '\\': turtle.rotation *= Quaternion.Euler(0, angle, 0); break;   // roll left (around Y)
                case '/': turtle.rotation *= Quaternion.Euler(0, -angle, 0); break;   // roll right
                case '|': turtle.rotation *= Quaternion.Euler(0, 0, 180); break;      // turn around

                case '[':
                    
                    stack.Push(turtle);
                    turtle.depth++;
                    turtle.length *= lengthRatio;
                    break;
                case 'L':
                    leaves.Add(MakeLeaf(turtle));
                    break;
                case ']':
                    
                    leaves.Add(MakeLeaf(turtle));
                    if (stack.Count > 0) turtle = stack.Pop();
                    break;
            }
        }
        return segments;
    }

    static Leaf MakeLeaf(State turtle)
    {
        Leaf leaf = new Leaf();
        leaf.position = turtle.position;
        leaf.rotation = turtle.rotation;
        return leaf;
    }
}
