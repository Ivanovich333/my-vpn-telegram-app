import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import axios from 'axios';
import { setUserProfile } from '../store/userSlice';

const useTelegramUser = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    const tg = window.Telegram.WebApp;

    if (!tg || !tg.initData) {
      console.error('Telegram WebApp data is not available.');
      return;
    }

    const verifyUser = async () => {
      try {
        console.log('Sending initData to server:', tg.initData);

        const response = await axios.get('/.netlify/functions/verifyAuth', {
          params: { initData: tg.initData },
        });

        if (response.data.ok) {
          const user = tg.initDataUnsafe.user;
          dispatch(
            setUserProfile({
              id: user.id,
              firstName: user.first_name,
              lastName: user.last_name,
              username: user.username,
              photoUrl: user.photo_url,
            })
          );
          console.log('User authenticated successfully');
        } else {
          console.error('Authentication failed:', response.data.error);
        }
      } catch (error) {
        console.error(
          'Error verifying user:',
          error.response ? error.response.data : error.message
        );
      }
    };

    verifyUser();
  }, [dispatch]);
};

export default useTelegramUser;
