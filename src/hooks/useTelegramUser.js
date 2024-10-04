import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import axios from 'axios';
import { setUserProfile } from '../store/userSlice';

const useTelegramUser = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    const tg = window.Telegram.WebApp;
    const initData = tg.initData;

    const verifyUser = async () => {
      try {
        const response = await axios.get('/.netlify/functions/verifyAuth', {
          params: tg.initDataUnsafe,
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
        } else {
          console.error('Authentication failed:', response.data.error);
        }
      } catch (error) {
        console.error('Error verifying user:', error);
      }
    };

    verifyUser();
  }, [dispatch]);
};

export default useTelegramUser;
