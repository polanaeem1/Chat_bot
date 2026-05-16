from datetime import time
import logging
import requests
def create_booking_api(payload: dict):
    max_retries = 2  # Fewer retries for booking to avoid duplicate bookings
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"https://donald-deadliest-jayla.ngrok-free.dev/api/Bookings",
                json=payload
                )
            print(payload)
            
            if response.status_code in (200, 201):
                return {
                    'success': True,
                    'message': 'Booking created successfully',
                    'data': response.json()
                }
            elif response.status_code == 400:
                return {
                    'success': False,
                    'error': 'Invalid booking request. Please check your details.'
                }
            elif response.status_code == 500:
                return {
                    'success': False,
                    'error': f'This spot is already occupied. Please choose another.{response.text}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Booking failed with status {response.status_code}'
                }
        
        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                logging.warning(f"Connection failed for booking (attempt {attempt + 1}/{max_retries}), retrying...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logging.error(f"Failed to create booking after {max_retries} attempts: {e}")
                return {
                    'success': False,
                    'error': 'Unable to connect to booking system. Please try again.'
                }
        except requests.RequestException as e:
            logging.error(f"Failed to create booking: {e}")
            return {
                'success': False,
                'error': 'Unable to connect to booking system. Please try again.'
            }
    
    return {
        'success': False,
        'error': 'Booking failed after multiple attempts.'
    }

print(create_booking_api(
    {'UserId': 'ABC123', 
    'ApplicationUserId': 'ABC123',
    'GarageId': 2, 
    'SlotNumber': "2", 
    'BookingStart': '2027-01-05T18:00:00',
    'BookingEnd': '2027-01-05T20:00:00',
    'PriorityApplied': False,
    'Price': 52.0
    }
    ))
