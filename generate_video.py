"""
generate_video.py — Fixed version
Large fonts, proper layout, working code slides, Windows-compatible temp paths.

Usage:
    pip install "moviepy==1.0.3" gtts pillow numpy
    python generate_video.py
"""

import os, textwrap, tempfile, numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

W, H      = 1920, 1080
FPS       = 24
CHART_DIR = r"C:\Users\Alamin\PycharmProjects\Process_Task-server\results\plots"
OUT_FILE  = "presentation.mp4"
TMP       = tempfile.gettempdir()

BG       = ( 10,  14,  26)
BG_CARD  = ( 18,  24,  42)
ACCENT   = ( 82, 183, 255)
ACCENT2  = (255, 107,  61)
WHITE    = (255, 255, 255)
GREY     = (160, 170, 190)
CODE_BG  = ( 15,  22,  40)
CODE_FG  = (180, 230, 140)
CODE_KW  = (130, 180, 255)
CODE_CMT = (100, 160, 100)
CODE_STR = (255, 180, 100)

_fc = {}

def font(size, bold=False):
    k = (size, bold)
    if k in _fc: return _fc[k]
    for p in [
        r"C:\Windows\Fonts\arialbd.ttf"  if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        if os.path.exists(p):
            f = ImageFont.truetype(p, size); _fc[k] = f; return f
    return ImageFont.load_default()

def mono(size):
    for p in [r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\cour.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return font(size)

def new_frame(bg=BG):
    img = Image.new("RGB", (W, H), bg)
    return img, ImageDraw.Draw(img)

def th(draw, text, fnt):
    b = draw.textbbox((0,0), text, font=fnt); return b[3]-b[1]

def wrap_draw(draw, text, x, y, max_w, fnt, fill=WHITE, sp=14):
    words = text.split(); lines, line = [], []
    for w in words:
        test = " ".join(line+[w])
        b = draw.textbbox((0,0), test, font=fnt)
        if b[2]-b[0] > max_w and line: lines.append(" ".join(line)); line=[w]
        else: line.append(w)
    if line: lines.append(" ".join(line))
    cy = y
    for l in lines:
        draw.text((x, cy), l, font=fnt, fill=fill)
        cy += th(draw, l, fnt) + sp
    return cy

def title_slide(title, subtitle="", tag=""):
    img, draw = new_frame()
    draw.rectangle([0,0,W,12], fill=ACCENT)
    draw.rectangle([0,H-12,W,H], fill=ACCENT2)
    draw.ellipse([W-480,-220,W+120,420], fill=(20,35,65))
    if tag:
        b = draw.textbbox((0,0), tag, font=font(38,True))
        draw.rectangle([80,175,80+b[2]-b[0]+44,245], fill=ACCENT)
        draw.text((102,183), tag, font=font(38,True), fill=BG)
    cy = 290
    for line in textwrap.wrap(title, 28):
        draw.text((80,cy), line, font=font(108,True), fill=WHITE); cy+=126
    if subtitle:
        cy += 24
        for line in textwrap.wrap(subtitle, 50):
            draw.text((80,cy), line, font=font(52), fill=GREY); cy+=70
    return np.array(img)

def bullet_slide(heading, bullets):
    img, draw = new_frame()
    draw.rectangle([0,0,W,12], fill=ACCENT)
    draw.rectangle([0,H-12,W,H], fill=ACCENT2)
    draw.text((80,32), heading, font=font(72,True), fill=ACCENT)
    draw.line([(80,120),(W-80,120)], fill=ACCENT, width=3)
    cy = 148
    for b in bullets:
        draw.ellipse([80,cy+16,118,cy+54], fill=ACCENT2)
        cy = wrap_draw(draw, b, 138, cy, W-220, font(46), fill=WHITE, sp=10)
        cy += 30
        if cy > H-80: break
    return np.array(img)

def code_slide(heading, code_lines, caption=""):
    img, draw = new_frame()
    draw.rectangle([0,0,W,12], fill=ACCENT)
    draw.rectangle([0,H-12,W,H], fill=ACCENT2)
    draw.text((80,22), heading, font=font(58,True), fill=ACCENT)
    box_top = 106
    box_bot = H-90 if not caption else H-148
    draw.rectangle([44,box_top,W-44,box_bot], fill=CODE_BG, outline=ACCENT, width=2)
    cy   = box_top+16
    mfnt = mono(36)
    nfnt = mono(28)
    for i, line in enumerate(code_lines, 1):
        if cy+44 > box_bot-8:
            draw.text((100,cy), "  ...", font=mfnt, fill=GREY); break
        draw.text((56,cy+4), f"{i:2d}", font=nfnt, fill=(70,90,120))
        s = line.lstrip()
        if s.startswith("#"):          fill=CODE_CMT
        elif any(s.startswith(k) for k in
                 ["def ","class ","import ","from ","return ","async "]):
                                       fill=CODE_KW
        elif s.startswith(("\"","'")):  fill=CODE_STR
        elif s.startswith(("}","{")):   fill=GREY
        else:                          fill=CODE_FG
        draw.text((106,cy), line, font=mfnt, fill=fill)
        cy += 44
    if caption:
        draw.text((80,H-132), caption, font=font(32), fill=GREY)
    return np.array(img)

def finding_slide(number, finding, evidence, implication):
    img, draw = new_frame(BG_CARD)
    draw.rectangle([0,0,W,12], fill=ACCENT)
    draw.rectangle([0,H-12,W,H], fill=ACCENT2)
    draw.text((80,24), f"#{number}", font=font(148,True), fill=ACCENT)
    draw.line([(80,210),(W-80,210)], fill=ACCENT, width=3)
    cy = 238
    cy = wrap_draw(draw, finding, 80, cy, W-160, font(66,True), fill=WHITE, sp=14)
    cy += 28
    draw.rectangle([44,cy,W-44,cy+118], fill=(25,38,65))
    draw.text((76,cy+10), "📊  Evidence:", font=font(36,True), fill=ACCENT2)
    wrap_draw(draw, evidence, 76, cy+54, W-160, font(36), fill=GREY, sp=8)
    cy += 136
    draw.text((80,cy), "→  "+implication, font=font(42), fill=ACCENT)
    return np.array(img)

def chart_slide(heading, chart_filename, caption=""):
    img, draw = new_frame()
    draw.rectangle([0,0,W,12], fill=ACCENT)
    draw.rectangle([0,H-12,W,H], fill=ACCENT2)
    draw.text((80,20), heading, font=font(56,True), fill=ACCENT)
    chart_path = os.path.join(CHART_DIR, chart_filename)
    if os.path.exists(chart_path):
        chart = Image.open(chart_path).convert("RGB")
        bw, bh = W-100, H-210
        chart.thumbnail((bw, bh), Image.LANCZOS)
        cx = (W-chart.width)//2
        cy_p = 96+(H-210-chart.height)//2
        img.paste(chart, (cx, cy_p))
        draw = ImageDraw.Draw(img)
    else:
        draw.text((W//2-300,H//2), f"[{chart_filename} not found]", font=font(42), fill=ACCENT2)
    if caption:
        draw.rectangle([0,H-108,W,H-12], fill=(15,22,40))
        draw.text((60,H-96), caption, font=font(32), fill=GREY)
    return np.array(img)

SLIDES = [
    (lambda: title_slide("OS Concurrency Study","Adaptive Task Execution Server","CSE 323 — Operating Systems"),
     "Most OS textbooks explain scheduling and concurrency in theory. This project runs it, measures it, and proves which combinations actually perform better, and why."),
    (lambda: bullet_slide("What We Built",[
        "An HTTP server that accepts jobs and executes them under different OS conditions",
        "2 scheduling policies: FIFO and Priority",
        "3 execution models: Thread Pool, Process Pool, and Async Event Loop",
        "5 workload types: CPU, IO, Memory, Mixed, and ML inference",
        "OS-level metrics per job: CPU time, context switches, memory — via psutil",
     ]),
     "We built a task execution server that separates three concerns: which job runs next, how it runs, and what work it does. This mirrors how real operating systems design their schedulers and executors."),
    (lambda: bullet_slide("Architecture",[
        "Request → Server → Scheduler → Dispatcher → Executor → Workload → Metrics",
        "Scheduler is policy-only: decides order, never executes",
        "Executor is mechanism-only: runs jobs, never decides order",
        "Dispatcher bridges both: makes waiting time independently measurable",
        "Every layer has exactly one responsibility — mirrors real OS design",
     ]),
     "The key architectural decision is separation of concerns. The scheduler only decides which job runs next. The executor only decides how to run it. The dispatcher sits between them and measures the exact waiting time. This is how real operating systems are designed."),
    (lambda: code_slide("Job Abstraction — src/core/job.py",[
        "# Every HTTP request becomes a Job object",
        "@dataclass",
        "class Job:",
        "    workload_type: str        # e.g. 'cpu_fibonacci'",
        "    params: Dict[str, Any]    # e.g. {'n': 32}",
        "    priority: int = 2         # 1=high  2=medium  3=low",
        "    created_at:  float        # arrival timestamp",
        "    enqueued_at: float        # when scheduler received it",
        "    dequeued_at: float        # when executor picked it up",
        "    waiting_time:   float     # dequeued_at - enqueued_at",
        "    execution_time: float     # completed_at - started_at",
        "    os_metrics: Dict          # CPU, ctx switches, memory",
        "    on_complete: Callable     # callback when job finishes",
     ],"Central data structure — tracks full job lifecycle"),
     "Every HTTP request is converted into a Job object. It captures the full lifecycle from arrival to completion. The waiting time field is the difference between when the scheduler received the job and when the executor picked it up. This is where we measure scheduler delay precisely."),
    (lambda: code_slide("Priority Scheduler — src/scheduler/priority.py",[
        "class PriorityScheduler:",
        "    def __init__(self):",
        "        self._heap = []",
        "        self._condition = threading.Condition()",
        "",
        "    def put(self, job):",
        "        job.mark_enqueued()",
        "        # id(job) prevents TypeError when timestamps tie",
        "        heapq.heappush(self._heap,",
        "            (job.priority, job.created_at, id(job), job))",
        "        self._condition.notify()",
        "",
        "    def get(self, timeout=None):",
        "        self._condition.wait(timeout=timeout)",
        "        _, _, _, job = heapq.heappop(self._heap)",
     ],"Two bugs fixed: id(job) tiebreaker + Condition to eliminate busy-wait"),
     "The priority scheduler uses a min-heap. Lower integer means higher priority. We had to add the job's memory address as a tiebreaker because Python would crash comparing Job objects when timestamps were identical. We also replaced a busy-wait loop with a threading Condition to prevent the dispatcher burning CPU while the queue is empty."),
    (lambda: code_slide("Live Request and Response",[
        "# POST /run",
        "{",
        '  "workload_type": "cpu_fibonacci",',
        '  "params": {"n": 32},',
        '  "priority": 1',
        "}",
        "",
        "# Response — real data from our experiment",
        "{",
        '  "execution_time": 0.312,',
        '  "waiting_time":   0.003,',
        '  "os_metrics": {',
        '    "cpu_user_delta_s":    0.297,',
        '    "ctx_voluntary_delta": 236,',
        '    "memory_delta_mb":     0.33',
        "  }",
        "}",
     ],"Every job returns OS-level measurements — not just latency"),
     "Here is a real request and response from our experiment. We submit a fibonacci calculation at high priority. The response shows execution time, waiting time in the queue, CPU seconds consumed, voluntary context switches, and memory allocated. All measured at the OS level."),
    (lambda: bullet_slide("Experiment Setup",[
        "7 configurations: baseline, thread+FIFO, thread+priority, process+FIFO, process+priority, async+FIFO, async+priority",
        "Locust load testing: 100 concurrent users, 3 minutes per configuration",
        "8 workload types submitted with realistic weights and priorities",
        "All results logged to JSONL — one line per completed job",
        "summarize.py aggregates, plot.py generates 5 charts from real data",
     ]),
     "To compare all configurations fairly we use Locust. 100 concurrent users submit randomized jobs for 3 minutes per configuration. Every single job is logged to JSON Lines format. After all seven runs we aggregate and generate charts."),
    (lambda: finding_slide("1",
        "Process executor is 43.6% faster than baseline for CPU",
        "cpu_fibonacci: baseline=0.550s   thread=0.520s   process=0.310s",
        "Python's GIL prevents threads from running CPU code in parallel."),
     "Finding one. The process executor is 43 percent faster than baseline for CPU workloads. Python has a Global Interpreter Lock — the GIL — which prevents multiple threads from executing Python code simultaneously. Separate processes each have their own GIL and run in true parallel on different cores. Our measurements prove this directly."),
    (lambda: chart_slide("Finding 1 — GIL Effect on CPU Workloads",
        "execution_time_by_executor.png",
        "Process dominates CPU workloads. Async slowest for CPU due to event-loop bridging overhead."),
     "This chart shows mean execution time per workload type for each executor. For CPU fibonacci, process is clearly the fastest. Thread is barely better than baseline due to the GIL. Async is the slowest because CPU work is offloaded to a thread pool internally."),
    (lambda: finding_slide("2",
        "Priority scheduling causes IO starvation — waiting time +212%",
        "io_sleep FIFO=0.008s vs Priority=0.025s at 100 concurrent users",
        "IO jobs starve as CPU jobs continuously skip the queue."),
     "Finding two. Priority scheduling increases IO waiting time by over 200 percent at high load. IO jobs have priority 3, the lowest. CPU jobs have priority 1, the highest. Under 100 concurrent users, CPU jobs continuously arrive and jump the queue ahead of IO jobs. This is textbook priority starvation — we measured it."),
    (lambda: chart_slide("Finding 2 — Priority Starvation",
        "waiting_time_by_scheduler.png",
        "IO jobs wait 80 to 212% longer under Priority vs FIFO at 100 concurrent users."),
     "This chart compares FIFO and Priority waiting times per workload type. IO sleep and IO file show the largest increases under Priority scheduling. CPU jobs benefit — their waiting time drops because they skip IO jobs. This is the fairness versus efficiency tradeoff in Chapter 5 of Silberschatz."),
    (lambda: finding_slide("3",
        "Async handles 2× more IO jobs per second than threads",
        "async: 3.22 jobs/s   thread: 1.78 jobs/s   process: 1.83 jobs/s",
        "Event loop concurrency — many IO waits overlap without blocking threads."),
     "Finding three. The async executor processes twice as many IO jobs per second as threads. The asyncio event loop handles IO waits cooperatively. When one coroutine awaits a file read or sleep, the loop immediately runs another. No thread is blocked and no context switch is needed. This is cooperative multitasking."),
    (lambda: chart_slide("Context Switches — OS Overhead per Executor",
        "ctx_switches_by_executor.png",
        "Process executor highest OS overhead — each job crosses a process boundary via IPC."),
     "Process executor generates the most voluntary context switches per job. Every job must cross a process boundary — the parent spawns a worker, the OS schedules it, and the parent waits for the result. This inter-process communication overhead is the cost of true CPU parallelism."),
    (lambda: chart_slide("Total Time — Executor × Scheduler",
        "total_time_heatmap.png",
        "Thread+FIFO: lowest latency. Async: highest throughput. Process+FIFO: best for CPU."),
     "The heatmap summarizes mean total time across all executor and scheduler combinations. Thread plus FIFO achieves the lowest per-job latency overall. Async appears slower per job but processes twice as many jobs concurrently. Process plus FIFO is optimal when CPU workloads dominate."),
    (lambda: bullet_slide("Textbook Mapping",[
        "GIL limits thread CPU parallelism → Chapter 4: Threads",
        "Process isolation enables true parallelism → Chapter 3: Processes",
        "FIFO vs Priority waiting time tradeoff → Chapter 5: CPU Scheduling",
        "Priority starvation under high load → Chapter 5: Scheduling Criteria",
        "Voluntary context switches from IO waits → Chapter 6: Synchronization",
        "Async event loop concurrency model → Chapter 13: IO Systems",
     ]),
     "Every finding maps directly to a chapter in Silberschatz. This project is not just code. It is a measurement instrument for the concepts in the textbook, with real data to support every claim."),
    (lambda: title_slide("Fully Open Source","Code · Docs · Experiments · Results · All on GitHub","github.com/galileo-gal"),
     "The full source code, architecture documentation, API reference, experiment procedure, and all results are available on GitHub. Every design decision is documented and every finding is traceable to raw data. Thank you."),
]

def make_audio(text, index):
    path = os.path.join(TMP, f"osc_audio_{index:02d}.mp3")
    gTTS(text=text, lang="en", slow=False).save(path)
    return path

def make_clip(frame_arr, audio_path, min_dur=4.0):
    audio    = AudioFileClip(audio_path)
    duration = max(audio.duration + 0.6, min_dur)
    return ImageClip(frame_arr, duration=duration).set_audio(audio)

def main():
    print(f"Generating {len(SLIDES)} slides...")
    clips = []
    for i, (render_fn, narration) in enumerate(SLIDES):
        print(f"  [{i+1:02d}/{len(SLIDES)}] rendering + TTS...", end=" ", flush=True)
        clip = make_clip(render_fn(), make_audio(narration, i))
        clips.append(clip)
        print(f"{clip.duration:.1f}s")
    print("\nAssembling final video...")
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        OUT_FILE, fps=FPS, codec="libx264", audio_codec="aac",
        temp_audiofile=os.path.join(TMP, "osc_temp_audio.m4a"),
        remove_temp=True, verbose=False, logger=None,
    )
    print(f"\nDone: {OUT_FILE}  ({sum(c.duration for c in clips)/60:.1f} min)")

if __name__ == "__main__":
    main()