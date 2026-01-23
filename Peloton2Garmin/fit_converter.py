"""
FIT Converter Module
Converts Peloton workout data to Garmin FIT format
"""

from datetime import datetime, timedelta
import struct


class PelotonToFitConverter:
    """Convert Peloton workouts to FIT files"""
    
    def __init__(self, peloton_auth):
        """
        Initialize converter
        
        Args:
            peloton_auth: PelotonAuthenticator instance
        """
        self.peloton_auth = peloton_auth
    
    def convert_workout_to_fit(self, workout, output_path):
        """
        Convert a Peloton workout to FIT format
        
        Args:
            workout: Workout dictionary from Peloton API
            output_path: Path to save the FIT file
        """
        # Debug: Print workout structure
        print(f"\n=== Workout Data ===")
        print(f"ID: {workout.get('id')}")
        print(f"Created: {workout.get('created_at')}")
        print(f"Start time: {workout.get('start_time')}")
        print(f"End time: {workout.get('end_time')}")
        print(f"Total work: {workout.get('total_work')}")
        
        ride = workout.get('ride', {})
        print(f"Ride title: {ride.get('title')}")
        print(f"Ride duration: {ride.get('duration')}")
        print(f"Ride discipline: {ride.get('fitness_discipline')}")
        print(f"===================\n")
        
        # Always use manual FIT creation for reliability
        try:
            self._create_fit_manually(workout, output_path)
        except Exception as e:
            print(f"FIT creation error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise
    
    def _create_fit_with_sdk(self, workout, output_path):
        """Create FIT file using Garmin FIT SDK"""
        try:
            from garmin_fit_sdk import Fit, Stream, Encoder
            from datetime import timezone
            
            # Create encoder
            fit = Fit()
            encoder = Encoder()
            
            # Get workout details
            ride = workout.get('ride', {})
            start_time = datetime.fromtimestamp(workout.get('created_at', 0))
            duration = ride.get('duration', 0)
            
            # File ID message
            file_id_msg = fit.file_id_mesg()
            file_id_msg.type = fit.file.value
            file_id_msg.manufacturer = 1  # Garmin
            file_id_msg.product = 0
            file_id_msg.time_created = int(start_time.timestamp() * 1000)
            
            encoder.write(file_id_msg)
            
            # Session message
            session_msg = fit.session_mesg()
            session_msg.timestamp = int(start_time.timestamp() * 1000)
            session_msg.start_time = int(start_time.timestamp() * 1000)
            
            # Map Peloton workout type to Garmin sport
            workout_type = ride.get('fitness_discipline', '').lower()
            if 'cycling' in workout_type or 'bike' in workout_type:
                session_msg.sport = fit.sport_cycling.value
                session_msg.sub_sport = fit.sub_sport_indoor_cycling.value
            elif 'running' in workout_type:
                session_msg.sport = fit.sport_running.value
                session_msg.sub_sport = fit.sub_sport_treadmill.value
            else:
                session_msg.sport = fit.sport_fitness_equipment.value
            
            session_msg.total_elapsed_time = duration
            session_msg.total_timer_time = duration
            session_msg.total_calories = workout.get('total_work', 0) // 1000
            
            encoder.write(session_msg)
            
            # Get performance data
            perf_data = self.peloton_auth.get_workout_performance_graph(workout.get('id'))
            
            if perf_data:
                self._add_performance_records(encoder, fit, start_time, perf_data)
            
            # Write to file
            with open(output_path, 'wb') as f:
                encoder.finish()
                f.write(encoder.bytes)
            
        except Exception as e:
            # Fallback to manual creation
            print(f"SDK creation failed: {e}, using manual method")
            self._create_fit_manually(workout, output_path)
    
    def _create_fit_manually(self, workout, output_path):
        """
        Create FIT file manually (fallback method)
        Creates a minimal but valid FIT file
        """
        # Get workout data with safe defaults
        ride = workout.get('ride', {})
        
        # Handle timestamp - ensure it's valid
        created_at = workout.get('created_at', 0)
        if created_at and created_at > 0:
            start_time = datetime.fromtimestamp(created_at)
        else:
            start_time = datetime.now()
        
        # Handle duration - ensure it's an integer
        duration = ride.get('duration', 0)
        if not duration or not isinstance(duration, (int, float)):
            duration = workout.get('end_time', 0) - workout.get('start_time', 0)
        duration = int(duration) if duration else 1800  # Default to 30 minutes
        
        # Handle calories - ensure it's an integer
        total_work = workout.get('total_work', 0)
        if isinstance(total_work, (int, float)):
            calories = int(total_work / 1000) if total_work > 0 else 0
        else:
            calories = 0
        
        # Ensure minimum values
        if duration < 1:
            duration = 60  # At least 1 minute
        if calories < 0:
            calories = 0
        
        # FIT file structure
        fit_data = bytearray()
        
        # FIT header (14 bytes)
        header_size = 14
        protocol_version = 0x20  # 2.0
        profile_version = 2132  # 21.32
        data_size = 0  # Will calculate later
        data_type = b'.FIT'
        
        # We'll build the data first, then add header
        messages = bytearray()
        
        # File ID message (required)
        file_id = self._create_file_id_message(start_time)
        messages.extend(file_id)
        
        # Session message
        session = self._create_session_message(workout, start_time, duration, calories)
        messages.extend(session)
        
        # Activity message
        activity = self._create_activity_message(start_time, duration)
        messages.extend(activity)
        
        # Calculate CRC
        data_size = len(messages)
        
        # Build header
        fit_data.append(header_size)
        fit_data.append(protocol_version)
        fit_data.extend(struct.pack('<H', profile_version))
        fit_data.extend(struct.pack('<I', data_size))
        fit_data.extend(data_type)
        
        # CRC of header (optional, set to 0)
        fit_data.extend(struct.pack('<H', 0))
        
        # Add messages
        fit_data.extend(messages)
        
        # Calculate and add CRC of entire file
        crc = self._calculate_crc(fit_data)
        fit_data.extend(struct.pack('<H', crc))
        
        # Write to file
        with open(output_path, 'wb') as f:
            f.write(fit_data)
    
    def _create_file_id_message(self, timestamp):
        """Create FIT file ID message"""
        msg = bytearray()
        
        # Definition message for file_id (global message 0)
        msg.append(0x40)  # Definition message, local message 0
        msg.append(0x00)  # Reserved
        msg.append(0x00)  # Architecture (little endian)
        msg.extend(struct.pack('<H', 0))  # Global message number (file_id)
        msg.append(4)  # Number of fields
        
        # Field definitions
        msg.append(0)  # type
        msg.append(1)  # size
        msg.append(0)  # base type (enum)
        
        msg.append(1)  # manufacturer
        msg.append(2)  # size
        msg.append(0x84)  # base type (uint16)
        
        msg.append(2)  # product
        msg.append(2)  # size
        msg.append(0x84)  # base type (uint16)
        
        msg.append(4)  # time_created
        msg.append(4)  # size
        msg.append(0x86)  # base type (uint32)
        
        # Data message
        msg.append(0x00)  # Data message, local message 0
        msg.append(4)  # type = activity
        msg.extend(struct.pack('<H', 1))  # manufacturer = garmin
        msg.extend(struct.pack('<H', 0))  # product
        
        # Convert timestamp to FIT time (seconds since Dec 31, 1989 UTC)
        fit_epoch = datetime(1989, 12, 31, 0, 0, 0)
        fit_time = int((timestamp - fit_epoch).total_seconds())
        # Ensure it's a valid unsigned 32-bit integer
        fit_time = max(0, min(fit_time, 0xFFFFFFFF))
        msg.extend(struct.pack('<I', fit_time))
        
        return msg
    
    def _create_session_message(self, workout, start_time, duration, calories):
        """Create FIT session message"""
        msg = bytearray()
        
        ride = workout.get('ride', {})
        workout_type = ride.get('fitness_discipline', '').lower()
        
        # Determine sport type
        if 'cycling' in workout_type or 'bike' in workout_type:
            sport = 2  # cycling
            sub_sport = 6  # indoor_cycling
        elif 'running' in workout_type:
            sport = 1  # running
            sub_sport = 1  # treadmill
        else:
            sport = 4  # fitness_equipment
            sub_sport = 0  # generic
        
        # Ensure all values are valid integers
        duration = int(duration)
        calories = int(calories)
        
        # Definition message for session (global message 18)
        msg.append(0x41)  # Definition message, local message 1
        msg.append(0x00)  # Reserved
        msg.append(0x00)  # Architecture (little endian)
        msg.extend(struct.pack('<H', 18))  # Global message number (session)
        msg.append(5)  # Number of fields
        
        # Field definitions
        msg.append(253)  # timestamp
        msg.append(4)
        msg.append(0x86)
        
        msg.append(2)  # start_time
        msg.append(4)
        msg.append(0x86)
        
        msg.append(7)  # total_elapsed_time
        msg.append(4)
        msg.append(0x86)
        
        msg.append(5)  # sport
        msg.append(1)
        msg.append(0)
        
        msg.append(11)  # total_calories
        msg.append(2)
        msg.append(0x84)
        
        # Data message
        msg.append(0x01)  # Data message, local message 1
        
        fit_epoch = datetime(1989, 12, 31, 0, 0, 0)
        fit_time = int((start_time - fit_epoch).total_seconds())
        fit_time = max(0, min(fit_time, 0xFFFFFFFF))
        
        msg.extend(struct.pack('<I', fit_time))  # timestamp
        msg.extend(struct.pack('<I', fit_time))  # start_time
        
        # Duration in milliseconds, ensure it's valid
        duration_ms = duration * 1000
        duration_ms = max(0, min(duration_ms, 0xFFFFFFFF))
        msg.extend(struct.pack('<I', duration_ms))  # total_elapsed_time (ms)
        
        msg.append(sport)  # sport
        
        # Calories must fit in uint16
        calories = max(0, min(calories, 65535))
        msg.extend(struct.pack('<H', calories))  # total_calories
        
        return msg
    
    def _create_activity_message(self, timestamp, duration):
        """Create FIT activity message"""
        msg = bytearray()
        
        # Ensure duration is valid
        duration = int(duration) if duration else 60
        
        # Definition message for activity (global message 34)
        msg.append(0x42)  # Definition message, local message 2
        msg.append(0x00)
        msg.append(0x00)
        msg.extend(struct.pack('<H', 34))  # Global message number (activity)
        msg.append(3)  # Number of fields
        
        msg.append(253)  # timestamp
        msg.append(4)
        msg.append(0x86)
        
        msg.append(1)  # num_sessions
        msg.append(2)
        msg.append(0x84)
        
        msg.append(2)  # type
        msg.append(1)
        msg.append(0)
        
        # Data message
        msg.append(0x02)  # Data message, local message 2
        
        fit_epoch = datetime(1989, 12, 31, 0, 0, 0)
        fit_time = int((timestamp - fit_epoch).total_seconds())
        fit_time = max(0, min(fit_time, 0xFFFFFFFF))
        
        msg.extend(struct.pack('<I', fit_time))
        msg.extend(struct.pack('<H', 1))  # num_sessions
        msg.append(0)  # type = manual
        
        return msg
    
    def _calculate_crc(self, data):
        """Calculate CRC-16 for FIT file"""
        crc = 0
        for byte in data:
            for _ in range(8):
                if (crc & 0x1) != (byte & 0x1):
                    crc = ((crc >> 1) & 0x7FFF) ^ 0xA001
                else:
                    crc = (crc >> 1) & 0x7FFF
                byte >>= 1
        return crc
    
    def _add_performance_records(self, encoder, fit, start_time, perf_data):
        """Add performance record messages"""
        # Extract metrics from performance data
        metrics = perf_data.get('metrics', [])
        
        for metric in metrics:
            if metric.get('slug') == 'heart_rate':
                values = metric.get('values', [])
                for i, value in enumerate(values):
                    if value is not None:
                        timestamp = start_time + timedelta(seconds=i)
                        
                        record_msg = fit.record_mesg()
                        record_msg.timestamp = int(timestamp.timestamp() * 1000)
                        record_msg.heart_rate = int(value)
                        
                        encoder.write(record_msg)


if __name__ == "__main__":
    print("FIT Converter Module")
    print("=" * 60)
    print("\nThis module converts Peloton workouts to Garmin FIT format.")
    print("Use it through the main application.")
