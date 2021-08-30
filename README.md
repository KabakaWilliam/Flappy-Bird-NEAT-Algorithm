# Flappy-Bird-NEAT-Algorithm
I implemented the NEAT algorithm to train a genetic neural network which plays flappy bird.
This involved building up the flappy bird game mechanics and graphics with pygame.

# Here's what it looks like

![numbers-min](https://github.com/KabakaWilliam/Flappy-Bird-NEAT-Algorithm/blob/main/flappyBird.gif)


## Running app
In your terminal, simply type:

```
python game.py
```

## Simplified Explanation of Algorithm
As you can see, the way the algorithm works is that it spawns a population of birds(10) with initially randomised weights.
By hitting the green poles or the ground, the spawned bird dies. So when all the birds die, we measure how far they got in the game and 
NEAT readjusts the Neural Network that controls the birds by either changing the weights or adding/dropping edges to mimic the bird that got the furthest.


Eventually the birds spawned will learn how to play the game without dying.

I found that by playing around with the population in ``` config.txt```,  the algorithm could immediately guess the right weights for the Neural Network for a couple of birds.


