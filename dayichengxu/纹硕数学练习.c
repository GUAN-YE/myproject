#include<stdio.h>
#include<stdlib.h>
#include<time.h>
main()
{  
int magic1,magic2 , s=1 ,x,t ,count=0;
 
char a;
 
     srand(time(NULL));

      
loop1:
	
 magic1=rand()%50+1;
		magic2= rand()%30+1;
		if(magic1<magic2)
		{
			magic1=magic2;
			magic2=magic1;
		}
		t=rand()%2+0;
		 
		if(t==0){a='+',s=magic1+magic2;}
		if(t==1){a='-',s=magic1-magic2;}
		 
	 printf("%d%c%d\n",magic1,a,magic2);
	 printf("输出答案: \n",x);
	scanf("%d",&x);
	if(s==x)   
	{
		printf("正确！纹硕真棒！\n ");
		goto  loop1;
		}
	else
	{
		printf("错了!重新答题\n");
	}
		do{
			printf("输出答案: \n",x);
	scanf("%d",&x);
	count++;
	if(s==x)
	{printf("正确!你真棒！继续答题！\n");
	goto loop1;
	}
	 
		}while(count!=4);
		printf("笨蛋！你连续错5次了！不跟你玩了！好好想想吧！");
     
	
}