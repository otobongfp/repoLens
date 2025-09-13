export default function LoadingSpinner() {
  return (
    <div className='mt-8 flex items-center justify-center'>
      <div className='border-primary h-10 w-10 animate-spin rounded-full border-b-2 border-t-2'></div>
    </div>
  );
}
