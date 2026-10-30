# Small-machine tutoring

The course uses tiny tables and CPU examples. A GPU and a full dataset download are unnecessary.

For a killed kernel, first preserve the learner's saved files and identify the exact cell. Read its input size and operations. Restart only the notebook kernel with the learner, then reproduce on fewer rows. Ask the learner to predict the smaller result before running it. Use one process and avoid concurrent model fits.

For PyTorch, use the CPU instructions in F20.4 and the five-point example in F20.5. Distinguish installation failure from a conceptual difficulty. Do not change system memory limits, WSL configuration, services or network settings. If a system change is required, explain what an administrator needs to do.
