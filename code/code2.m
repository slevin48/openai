
x = linspace(0,2*pi,100); % create x values
y = sin(x); % create y values from sine function
m = length(y); % length of y values
X = [ones(m,1), x']; % design matrix
beta = (X'*X)\X'*y'; % calculate regression coefficients
y_hat = X*beta; % predict y values using regression coefficients

plot(x,y,'bo',x,y_hat,'r-') % plot original function and regression line