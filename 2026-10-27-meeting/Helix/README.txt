Helix - Figures 1-12

Source: ASPLOS25_Helix.pdf (17 pages).
Helix: Serving Large Language Models over Heterogeneous GPUs and Network via Max-Flow
Yixuan Mei et al., ASPLOS 2025. DOI: 10.1145/3669940.3707215
Original paper: Creative Commons Attribution International 4.0.

All 12 PNGs (Figures 1-12) in the root of this folder include the original figure captions.
The figure-only versions and the caption-free overview image have been removed.
Each figure keeps all subpanels, axes, legends, and in-figure annotations.
Images are rendered from the original PDF at 600 DPI, cropped and padded with white margins.
No diagrams were redrawn and no labels or data were changed.
Tables are excluded because the request is for figures.

Figure | PDF page | Printed page | File including original caption
01 | 4 | 589 | Helix_Figure_01_Model_Placement_Examples_with_caption.png
02 | 4 | 589 | Helix_Figure_02_Max_Flow_Graph_Abstraction_with_caption.png
03 | 7 | 592 | Helix_Figure_03_System_Overview_with_caption.png
04 | 8 | 593 | Helix_Figure_04_Per_Request_Pipeline_Scheduling_with_caption.png
05 | 8 | 593 | Helix_Figure_05_Azure_Conversation_Statistics_with_caption.png
06 | 9 | 594 | Helix_Figure_06_Single_Cluster_Results_with_caption.png
07 | 10 | 595 | Helix_Figure_07_Geo_Distributed_Cluster_Results_with_caption.png
08 | 10 | 595 | Helix_Figure_08_High_GPU_Heterogeneity_Results_with_caption.png
09 | 11 | 596 | Helix_Figure_09_Model_Placement_Comparison_with_caption.png
10 | 12 | 597 | Helix_Figure_10_Request_Scheduling_Comparison_with_caption.png
11 | 12 | 597 | Helix_Figure_11_MILP_Optimization_Ablation_with_caption.png
12 | 13 | 598 | Helix_Figure_12_MILP_Solution_Quality_with_caption.png

ORIGINAL FIGURE CAPTIONS

Figure 1. Examples of sub-optimal model placement and request schedule. 1a) all GPUs and network condition in this example.
The order of compute capacity is: A100 > L4 > T4; 1b) Model placement by uniformly partition the model, then allocate devices
by a balanced compute capacity; 1c) Co-optimizing model partition and device placement to make the compute capacity more
balanced; 1d) Co-optimizing model partition, device placement, and request scheduling in a network-aware way.

Figure 2. Graph abstraction of a 3-node cluster with given
model placement. Numbers on the edges in Fig. 2b represent
their capacity, which is the number of tokens that can pass
through the edges per second. Max flow between source and
sink equals the max serving throughput of the cluster.

Figure 3. Helix overview. In Helix, the coordinator plans model placement as described in Sec. 4.4. We only need to run
model placement once for each cluster. When a new request arrives, the coordinator node runs Helix scheduler to assign it a
per-request pipeline and sends it to the first node in the pipeline. Each compute node in the pipeline performs inference on the
request on the layers it is responsible for and sends the (output for the) request to the next node in the pipeline. When the last
node in the pipeline finishes performing inference on its layers, it will send the output token for the request to the coordinator
(Worker Finished). The coordinator schedules generation of the next token for the request using the same pipeline.

Figure 4. Topology graph of a cluster, where each vertex is a
compute node, and each edge is a valid network connection.
Numbers over edges represent the flow over the network
connection in the max flow solution. The pipelines used to
schedule requests 1 and 2 are shown on the right.

Figure 5. Statistics of Azure Conversation dataset.

Figure 6. Single cluster results: (a - d) decode throughput, (e - h) prompt and decode latency for online serving. The box
shows the 25 and 75 percentile. The whisker shows the 5 and 95 percentile. The red line shows median.

Figure 7. Geo-distributed clusters: (a - b) decode throughput, (c - f) prompt and decode latency for online serving. "H"
stands for Helix, "S" stands for Swarm. Box: 25 and 75 percentile. Whisker: 5 and 95 percentile. Red line: median.

Figure 8. High GPU-heterogeneity clusters setup: (a)
decode throughput, (b - c) prompt and decode latency for
online serving. "H" stands for Helix, "S" stands for Swarm.

Figure 9. (a) Comparing different model placement methods with offline serving of LLaMA 70B. (b) The case study shows
model placements for serving LLaMA 70B on the single cluster setup.

Figure 10. (a) Comparing different request scheduling methods with offline serving of LLaMA 70B. (b) A case study that
illustrates the congestion in Swarm and random scheduling when serving LLaMA 70B in geo-distributed clusters setup.

Figure 11. Ablation study on MILP optimization.

Figure 12. Best solution and best upper bound found by
the MILP solver relative to solving time. The red dotted line
marks the optimal throughput for this cluster.
