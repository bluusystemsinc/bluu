#ifndef BLUUSINGLETON_H
#define BLUUSINGLETON_H

template <class T>
class CBluuSingleton
{
private:
  static T* m_pInstance;

private:
  CBluuSingleton( CBluuSingleton const& );
  CBluuSingleton& operator = ( CBluuSingleton const& );

protected:
  CBluuSingleton( void );
  ~CBluuSingleton( void );

public:
  static T* Instance()
  {
      if( !m_pInstance )
      {
        m_pInstance = new T;
      }

      return m_pInstance;
  }
};

template <class T>
T* CBluuSingleton<T>::m_pInstance = NULL;

#endif // BLUUSINGLETON_H
