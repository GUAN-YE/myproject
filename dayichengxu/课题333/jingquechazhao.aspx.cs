using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Data;
using System.Data.SqlClient;

public partial class jingquechazhao : System.Web.UI.Page
{
    SqlConnection aaa = new SqlConnection("server=.;database=keti;uid=liubin;pwd=123;");
    protected void Page_Load(object sender, EventArgs e)
    {
        string name = Request.QueryString["bn"];
        string writer = Request.QueryString["an"];
        string price1 = Request.QueryString["pn1"];
        string price2 = Request.QueryString["pn2"];
        if (price1 != "" && price2 != "")
        {
            aaa.Open();
            SqlDataAdapter adt = new SqlDataAdapter("select tupian, jiage,xinghao,xiaoliang,pinpai,kucun from tupian1 where xinghao like'%" + name + "%'and  pinpai like'%" + writer + "%'", aaa);
            DataTable dt = new DataTable();
            adt.Fill(dt);
            this.GridView1.DataSource = dt;
            this.GridView1.DataBind();
            aaa.Close();
        }
        else
        {
            aaa.Open();
            SqlDataAdapter adt = new SqlDataAdapter("select tupian,jiage,xinghao,xiaoliang,pinpai,kucun from tupian1 where xinghao like'%" + name + "%'and  pinpai like'%" + writer + "%'", aaa);
            DataTable dt = new DataTable();
            adt.Fill(dt);
            this.GridView1.DataSource = dt;
            this.GridView1.DataBind();
            aaa.Close();
        }
    }
     
}