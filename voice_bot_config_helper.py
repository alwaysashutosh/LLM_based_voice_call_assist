"""
Voice Bot Configuration Helper
==============================

This script uses diagnostic results to automatically configure the voice bot
with optimal audio settings based on the detected hardware and capabilities.
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime

def load_diagnostic_report(report_path: str = None) -> Dict:
    """Load the most recent diagnostic report"""
    if report_path and os.path.exists(report_path):
        with open(report_path, 'r') as f:
            return json.load(f)
    
    # Find the most recent report
    reports = [f for f in os.listdir('.') if f.startswith('voice_bot_audio_report_') and f.endswith('.json')]
    if not reports:
        raise FileNotFoundError("No diagnostic reports found. Run voice_bot_audio_diagnostics.py first.")
    
    latest_report = max(reports, key=lambda x: os.path.getctime(x))
    print(f"Loading diagnostic report: {latest_report}")
    
    with open(latest_report, 'r') as f:
        return json.load(f)

def get_optimal_device(report: Dict) -> Optional[Dict]:
    """Get the optimal microphone device from diagnostic results"""
    devices = report.get('devices', [])
    working_devices = [d for d in devices if d.get('working', False) and d.get('max_input_channels', 0) > 0]
    
    if not working_devices:
        return None
    
    # Prefer built-in microphones over Bluetooth devices
    built_in_devices = [d for d in working_devices if 'array' in d['name'].lower() or 'built' in d['name'].lower()]
    if built_in_devices:
        return built_in_devices[0]
    
    # Fall back to first working device
    return working_devices[0]

def get_optimal_audio_config(report: Dict) -> Dict:
    """Generate optimal audio configuration based on diagnostic results"""
    device = get_optimal_device(report)
    format_test = report.get('format_test', {})
    
    config = {
        'device_index': device['index'] if device else 0,
        'device_name': device['name'] if device else 'Default',
        'sample_rate': 16000,  # Default for voice recognition
        'channels': 1,  # Mono for voice
        'format': 'pyaudio.paInt16',  # Most compatible format
        'chunk_size': 1024,
        'exception_on_overflow': False,
        'recommendations': []
    }
    
    # Use compatible sample rates if available
    compatible_rates = format_test.get('compatible_rates', [])
    if 16000 in compatible_rates:
        config['sample_rate'] = 16000
    elif 22050 in compatible_rates:
        config['sample_rate'] = 22050
    elif 44100 in compatible_rates:
        config['sample_rate'] = 44100
    elif compatible_rates:
        config['sample_rate'] = compatible_rates[0]
    
    # Use device's default sample rate if it's compatible
    if device and device.get('default_sample_rate'):
        device_rate = int(device['default_sample_rate'])
        if device_rate in compatible_rates:
            config['sample_rate'] = device_rate
    
    # Add recommendations
    if device:
        config['recommendations'].append(f"Using device: {device['name']}")
    else:
        config['recommendations'].append("No optimal device found, using default")
    
    if config['sample_rate'] != 16000:
        config['recommendations'].append(f"Using sample rate {config['sample_rate']}Hz (16000Hz preferred for voice)")
    
    return config

def generate_pipecat_config(config: Dict) -> str:
    """Generate PipeCat configuration code"""
    return f'''
# PipeCat Audio Configuration (Generated from diagnostics)
audio_params = LocalAudioTransportParams(
    audio_in_sample_rate={config['sample_rate']},
    audio_out_sample_rate=24000,
    audio_in_channels={config['channels']},
    audio_out_channels=1,
    audio_in_device_name={config['device_index']},
    audio_out_device_name=3,  # Adjust based on your speakers
)
'''

def generate_pyaudio_config(config: Dict) -> str:
    """Generate PyAudio configuration code"""
    return f'''
# PyAudio Configuration (Generated from diagnostics)
import pyaudio

p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels={config['channels']},
    rate={config['sample_rate']},
    input=True,
    input_device_index={config['device_index']},
    frames_per_buffer={config['chunk_size']},
    exception_on_overflow={config['exception_on_overflow']}
)
'''

def generate_config_file(config: Dict, output_file: str = 'voice_bot_config.py'):
    """Generate a complete configuration file"""
    config_code = f'''#!/usr/bin/env python3
"""
Voice Bot Audio Configuration
============================

Auto-generated configuration based on audio diagnostics.
Generated on: {datetime.now().isoformat()}
Device: {config['device_name']}
Sample Rate: {config['sample_rate']}Hz
"""

# Audio Configuration
AUDIO_CONFIG = {json.dumps(config, indent=2)}

# PipeCat Configuration
def get_pipecat_audio_params():
    """Get PipeCat audio parameters"""
    from pipecat.transports.local.audio import LocalAudioTransportParams
    
    return LocalAudioTransportParams(
        audio_in_sample_rate={config['sample_rate']},
        audio_out_sample_rate=24000,
        audio_in_channels={config['channels']},
        audio_out_channels=1,
        audio_in_device_name={config['device_index']},
        audio_out_device_name=3,  # Adjust based on your speakers
    )

# PyAudio Configuration
def get_pyaudio_config():
    """Get PyAudio configuration"""
    import pyaudio
    
    return {{
        'format': pyaudio.paInt16,
        'channels': {config['channels']},
        'rate': {config['sample_rate']},
        'input': True,
        'input_device_index': {config['device_index']},
        'frames_per_buffer': {config['chunk_size']},
        'exception_on_overflow': {config['exception_on_overflow']}
    }}

# Usage Example
if __name__ == "__main__":
    print("Voice Bot Audio Configuration")
    print("=" * 40)
    print(f"Device: {{AUDIO_CONFIG['device_name']}}")
    print(f"Sample Rate: {{AUDIO_CONFIG['sample_rate']}}Hz")
    print(f"Channels: {{AUDIO_CONFIG['channels']}}")
    print(f"Device Index: {{AUDIO_CONFIG['device_index']}}")
    print()
    print("Recommendations:")
    for rec in AUDIO_CONFIG['recommendations']:
        print(f"  - {{rec}}")
'''
    
    with open(output_file, 'w') as f:
        f.write(config_code)
    
    print(f"Configuration saved to: {output_file}")

def main():
    """Main function to generate configuration"""
    print("Voice Bot Configuration Helper")
    print("=" * 40)
    
    try:
        # Load diagnostic report
        report = load_diagnostic_report()
        
        # Generate optimal configuration
        config = get_optimal_audio_config(report)
        
        print(f"Optimal Device: {config['device_name']}")
        print(f"Sample Rate: {config['sample_rate']}Hz")
        print(f"Channels: {config['channels']}")
        print(f"Device Index: {config['device_index']}")
        print()
        
        # Show recommendations
        print("Recommendations:")
        for rec in config['recommendations']:
            print(f"  - {rec}")
        print()
        
        # Generate configuration file
        generate_config_file(config)
        
        # Show usage examples
        print("Usage Examples:")
        print("=" * 40)
        print()
        print("1. For PipeCat:")
        print(generate_pipecat_config(config))
        print()
        print("2. For PyAudio:")
        print(generate_pyaudio_config(config))
        print()
        print("3. Import configuration:")
        print("from voice_bot_config import get_pipecat_audio_params, get_pyaudio_config")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Please run voice_bot_audio_diagnostics.py first to generate a diagnostic report.")

if __name__ == "__main__":
    main()
