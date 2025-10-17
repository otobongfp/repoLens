import React from 'react';

export interface StaggeredCardsProps {
  children: React.ReactNode;
}

const StaggeredCards: React.FC<StaggeredCardsProps> = ({ children }) => {
  return (
    <div className='relative origin-center -translate-x-3 rotate-6 p-6 duration-500 hover:rotate-0'>
      <span className='border-primary bg-card/10 hover:bg-card/15 absolute inset-0 border border-dashed'></span>
      <p className='text-muted-foreground'>{children}</p>
      <svg
        width='5'
        height='5'
        viewBox='0 0 5 5'
        className='fill-primary absolute left-[-2px] top-[-2px]'
      >
        <path d='M2 0h1v2h2v1h-2v2h-1v-2h-2v-1h2z'></path>
      </svg>
      <svg
        width='5'
        height='5'
        viewBox='0 0 5 5'
        className='fill-primary absolute right-[-2px] top-[-2px]'
      >
        <path d='M2 0h1v2h2v1h-2v2h-1v-2h-2v-1h2z'></path>
      </svg>
      <svg
        width='5'
        height='5'
        viewBox='0 0 5 5'
        className='fill-primary absolute bottom-[-2px] left-[-2px]'
      >
        <path d='M2 0h1v2h2v1h-2v2h-1v-2h-2v-1h2z'></path>
      </svg>
      <svg
        width='5'
        height='5'
        viewBox='0 0 5 5'
        className='fill-primary absolute bottom-[-2px] right-[-2px]'
      >
        <path d='M2 0h1v2h2v1h-2v2h-1v-2h-2v-1h2z'></path>
      </svg>
    </div>
  );
};

export default StaggeredCards;
