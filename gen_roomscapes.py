import spatialscaper as ss
import random
import os
import numpy as np
from pathlib import Path

# Constants
DURATION = 60  # 1 minute duration
SOUND_DIR = "datasets/sound_event_datasets/FSD50K_FMA"
RIR_DIR = "datasets/rir_datasets/"
OUTPUT_DIR = "output/soundscapes"
SR = 24000
REF_DB = -50
SNR_RANGE = (5, 7)  # 5-7 dB SNR range
TIME_SLOTS = 4  # Split duration into slots for better event distribution

# Event distribution (percentages) - Modify these as needed
EVENT_DISTRIBUTION = {
    # "clapping": 15,      #class 2
    # "telephone": 10,     #class 3
    # "laughter": 10,      #class 4
    # "footsteps": 15,     #class 6
    "doorCupboard": 10,  #class 7
    # "waterTap": 15,      #class 10
    "bell": 10,          #class 11
    # "knock": 15          #class 12
}

def get_foa_rooms():
    """Get available FOA format rooms from spatialscaper_RIRs"""
    sofa_dir = Path(RIR_DIR) / "spatialscaper_RIRs"
    foa_rooms = [f.stem.replace('_foa', '') for f in sofa_dir.glob('*_foa.sofa')]
    return foa_rooms

def generate_soundscape(idx, available_rooms):
    """Generate a single soundscape with controlled event distribution"""
    room = random.choice(available_rooms)
    n_events = random.randint(5, 15)  # Random number between 5-15 events
    
    # Initialize Scaper
    ssc = ss.Scaper(
        duration=DURATION,
        foreground_dir=SOUND_DIR,
        rir_dir=RIR_DIR,
        fmt="foa",
        room=room,
        max_event_overlap=2,
        ref_db=REF_DB,
        DCASE_format=True
    )

    # Add background ambient noise
    ssc.add_background()

    # Split duration into time slots for better event distribution
    time_slots = np.linspace(0, DURATION, TIME_SLOTS + 1)
    events_per_slot = n_events // TIME_SLOTS + 1
    
    events_added = 0
    for slot_idx in range(TIME_SLOTS):
        start_time = time_slots[slot_idx]
        end_time = time_slots[slot_idx + 1]
        
        # Add events for this time slot
        for _ in range(min(events_per_slot, n_events - events_added)):
            # Select event type based on distribution
            event_type = random.choices(
                list(EVENT_DISTRIBUTION.keys()),
                weights=list(EVENT_DISTRIBUTION.values())
            )[0]
            
            # Add event with specified parameters
            ssc.add_event(
                label=("const", event_type),
                source_file=("choose", []),
                source_time=("const", 0),
                event_time=("uniform", start_time, end_time),
                event_position=("const", ("uniform", None, None)),  # Static position
                snr=("uniform", SNR_RANGE[0], SNR_RANGE[1])
            )
            events_added += 1
            
            if events_added >= n_events:
                break
    
    # Generate filenames with important parameters
    filename = f"{room}_n{n_events}_snr{SNR_RANGE[0]}-{SNR_RANGE[1]}_{idx:03d}"
    audiofile = os.path.join(OUTPUT_DIR, "audio", filename)
    labelfile = os.path.join(OUTPUT_DIR, "labels", filename)
    
    # Generate the soundscape
    ssc.generate(audiofile, labelfile)
    return filename

def main(num_clips=900):
    """Generate multiple soundscapes"""
    # Create output directories
    os.makedirs(os.path.join(OUTPUT_DIR, "audio"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "labels"), exist_ok=True)
    
    # Get available FOA rooms
    available_rooms = get_foa_rooms()
    print(f"Found FOA rooms: {available_rooms}")
    
    # Generate soundscapes
    print(f"Generating {num_clips} soundscapes...")
    for i in range(num_clips):
        try:
            filename = generate_soundscape(i, available_rooms)
            print(f"Generated soundscape {i+1}/{num_clips}: {filename}")
        except Exception as e:
            print(f"Failed to generate soundscape {i+1}: {str(e)}")
            continue

if __name__ == "__main__":
    main()