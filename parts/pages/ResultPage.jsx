function ResultPage() {
  const params = new URLSearchParams(window.location.search);
  const status = params.get('status') || 'success';
  const ok = status === 'success';
  const order = params.get('order') || 'ST' + Date.now();
  const amount = params.get('amount') || '0';
  const plan = params.get('plan') || '专业版';
  const method = params.get('method') || '支付宝';

  return (
    <>
      <SubNav current="" />
      <div className="result-center">
        <div className="result-card">
          <div className={`result-icon ${ok ? 'ok' : 'fail'}`}>
            {ok ? (
              <svg viewBox="0 0 24 24" fill="none" width="32" height="32"><path d="M6 12l4 4 8-8" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" width="32" height="32"><path d="M6 6l12 12M18 6L6 18" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"/></svg>
            )}
          </div>
          <h2 className="cn">{ok ? '支付成功' : '支付未完成'}</h2>
          <p className="sub cn">{ok ? '感谢您的购买，授权信息将通过邮箱发送。' : '订单未完成或已取消，如需帮助请联系支持。'}</p>

          <div className="result-details">
            <div className="summary-row"><span className="label">订单号</span><span className="value" style={{fontFamily:'var(--font-mono)',fontSize:13}}>{order}</span></div>
            <div className="summary-row"><span className="label cn">套餐</span><span className="value cn">{plan}</span></div>
            <div className="summary-row"><span className="label">金额</span><span className="value">¥{amount}</span></div>
            <div className="summary-row"><span className="label cn">支付方式</span><span className="value cn">{method}</span></div>
          </div>

          <div className="result-actions">
            <a className="btn btn-accent" href="Download.html">前往下载</a>
            <a className="btn btn-ghost" href="Account.html">查看用户中心</a>
          </div>
        </div>
      </div>
      <SubFooter />
    </>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<ResultPage />);
